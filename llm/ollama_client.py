import requests
import json

from config import OLLAMA_BASE_URL, LLM_MODEL


class OllamaClient:

    def __init__(self):

        self.base_url = OLLAMA_BASE_URL.rstrip("/")
        self.model = LLM_MODEL

    def chat_stream(self, messages):

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,

            # IMPORTANT
            "stream": True,

            "keep_alive": "30m",

            "options": {
                        "temperature": 0.76,
                        "top_p": 0.9,
                        "repeat_penalty": 1.3,
                        "num_ctx": 4096,
                        "num_predict": 100,
                    }
        }

        try:

            with requests.post(
                url,
                json=payload,
                stream=True,
                timeout=(10, 180),
            ) as response:

                response.raise_for_status()

                buffered_start = ""
                emitted_any = False

                for line in response.iter_lines():

                    if not line:
                        continue

                    data = json.loads(
                        line.decode("utf-8")
                    )

                    if "message" in data:

                        token = data["message"].get(
                            "content",
                            ""
                        )

                        if token:

                            # ------------------------------------------
                            # Strip a leading wrapping quote the first
                            # time we see non-empty content, without
                            # delaying the rest of the stream.
                            # ------------------------------------------
                            if not emitted_any:

                                buffered_start += token

                                stripped_lead = buffered_start.lstrip()

                                # Wait for at least one non-space char
                                # before deciding whether to strip it.
                                if stripped_lead:

                                    if stripped_lead[0] in ('"', "\u201c"):
                                        stripped_lead = stripped_lead[1:]

                                    emitted_any = True
                                    yield stripped_lead

                                # else: keep buffering (all-whitespace so far)

                            else:
                                yield token

                    if data.get("done", False):

                        # Flush anything still buffered (e.g. token
                        # stream ended before any non-whitespace char
                        # arrived, which shouldn't normally happen).
                        if not emitted_any and buffered_start:
                            yield buffered_start

                        break

        except requests.exceptions.Timeout:

            yield (
                "\n\n⚠️ The local AI model "
                "took too long to respond."
            )

        except requests.exceptions.ConnectionError:

            yield (
                "\n\n⚠️ Unable to connect "
                "to the local Ollama service."
            )

        except requests.exceptions.RequestException as e:

            yield f"\n\n⚠️ Ollama request failed: {e}"

        except (ValueError, KeyError) as e:

            yield f"\n\n⚠️ Invalid Ollama response: {e}"