import json
import requests

from config import (
    ANALYZER_OLLAMA_BASE_URL,
    ANALYZER_LLM_MODEL,
)
ANALYZER_NUM_CTX = 8192

ANALYZER_NUM_PREDICT = 1800

ANALYZER_TEMPERATURE = 0.1

ANALYZER_TIMEOUT = 300


class SessionAnalyzerOllamaClient:

    """
    Dedicated Ollama client for Session Analyzer.

    This client is intentionally separate from the
    live training OllamaClient.

    Live training:
        llm/ollama_client.py

    Session analysis:
        llm/session_analyzer_client.py
    """

    def __init__(self):

        self.base_url = (
            ANALYZER_OLLAMA_BASE_URL
            .rstrip("/")
        )

        self.model = ANALYZER_LLM_MODEL

    # ========================================================
    # ANALYZE
    # ========================================================

    def analyze(self, messages):

        url = (
            f"{self.base_url}/api/chat"
        )

        payload = {

            "model":
                self.model,

            "messages":
                messages,

            "stream":
                False,

            "keep_alive":
                "30m",

            "options": {

                "temperature":
                    ANALYZER_TEMPERATURE,

                "num_ctx":
                    ANALYZER_NUM_CTX,

                "num_predict":
                    ANALYZER_NUM_PREDICT,

            },

            # Ask Ollama for structured JSON.
            "format":
                "json",

        }

        try:

            response = requests.post(

                url,

                json=payload,

                timeout=(
                    10,
                    ANALYZER_TIMEOUT,
                ),

            )

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