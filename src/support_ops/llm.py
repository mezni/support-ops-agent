from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from support_ops.config import Settings


T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def chat(self, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.openrouter_model,
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
        )

        return response.choices[0].message.content or ""

    def structured(
        self,
        user_message: str,
        output_model: type[T],
    ) -> T:
        response = self.client.chat.completions.parse(
            model=self.settings.openrouter_model,
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            response_format=output_model,
        )

        parsed = response.choices[0].message.parsed

        if parsed is None:
            raise ValueError("Model returned no structured output")

        return parsed
