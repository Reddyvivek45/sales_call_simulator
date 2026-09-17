import json
import requests
import time

from config import (
    ANALYZER_OLLAMA_BASE_URL,
    ANALYZER_LLM_MODEL,
)


# Session Analyzer configuration
ANALYZER_NUM_CTX = 8192
ANALYZER_NUM_PREDICT = 1800
ANALYZER_TEMPERATURE = 0.1
ANALYZER_TIMEOUT = 300


class SessionAnalyzerOllamaClient:

    """
    Dedicated Ollama client for Session Analyzer.

    Live training:
        llm/ollama_client.py

    Session analysis:
        llm/session_analyzer_client.py
    """

    def __init__(self):

        self.base_url = ANALYZER_OLLAMA_BASE_URL.rstrip("/")
        self.model = ANALYZER_LLM_MODEL

    def analyze(self, messages):

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": "30m",

            "options": {
                "temperature": ANALYZER_TEMPERATURE,
                "num_ctx": ANALYZER_NUM_CTX,
                "num_predict": ANALYZER_NUM_PREDICT,
            },

            "format": "json",
        }

        # -----------------------------------------
        # REQUEST INFORMATION
        # -----------------------------------------

        prompt_chars = sum(
            len(message.get("content", ""))
            for message in messages
        )

        print("\n" + "=" * 70)
        print("[ANALYZER] LLM REQUEST")
        print("=" * 70)

        print(f"Model           : {self.model}")
        print(f"Messages        : {len(messages)}")
        print(f"Prompt chars    : {prompt_chars:,}")
        print(f"num_ctx         : {ANALYZER_NUM_CTX}")
        print(f"num_predict     : {ANALYZER_NUM_PREDICT}")
        print(f"temperature     : {ANALYZER_TEMPERATURE}")

        start_time = time.perf_counter()

        try:

            response = requests.post(
                url,
                json=payload,
                timeout=(10, ANALYZER_TIMEOUT),
            )

            request_time = time.perf_counter() - start_time

            response.raise_for_status()

            data = response.json()

            content = (
                data
                .get("message", {})
                .get("content", "")
            )

            if not content:
                raise RuntimeError(
                    "Analyzer LLM returned an empty response."
                )

            total_time = time.perf_counter() - start_time

            # -----------------------------------------
            # TIMING INFORMATION
            # -----------------------------------------

            print("\n[ANALYZER] OLLAMA TIMING")
            print("-" * 70)

            print(f"HTTP request time : {request_time:.2f} sec")
            print(f"Total LLM time    : {total_time:.2f} sec")

            if "total_duration" in data:
                print(
                    f"Total duration    : "
                    f"{data['total_duration'] / 1e9:.2f} sec"
                )

            if "load_duration" in data:
                print(
                    f"Model load        : "
                    f"{data['load_duration'] / 1e9:.2f} sec"
                )

            if "prompt_eval_duration" in data:
                print(
                    f"Prompt eval       : "
                    f"{data['prompt_eval_duration'] / 1e9:.2f} sec"
                )

            if "eval_duration" in data:
                print(
                    f"Generation        : "
                    f"{data['eval_duration'] / 1e9:.2f} sec"
                )

            if "prompt_eval_count" in data:
                print(
                    f"Prompt tokens     : "
                    f"{data['prompt_eval_count']}"
                )

            if "eval_count" in data:
                print(
                    f"Output tokens     : "
                    f"{data['eval_count']}"
                )

            print(f"Output chars      : {len(content):,}")

            print("=" * 70)

            return content

        except requests.exceptions.Timeout:

            raise RuntimeError(
                "Session Analyzer LLM timed out."
            )

        except requests.exceptions.ConnectionError:

            raise RuntimeError(
                "Unable to connect to the "
                "Session Analyzer Ollama service."
            )

        except requests.exceptions.HTTPError as exc:

            raise RuntimeError(
                f"Analyzer Ollama HTTP error: {exc}"
            )

        except requests.exceptions.RequestException as exc:

            raise RuntimeError(
                f"Analyzer Ollama request failed: {exc}"
            )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                f"Invalid response from Analyzer Ollama: {exc}"
            )