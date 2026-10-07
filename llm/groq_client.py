import os
from groq import Groq

from config import GROQ_MODEL


class GroqClient:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable is not set."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = GROQ_MODEL

    def chat_stream(self, messages):

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=300,
            stream=True,
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content