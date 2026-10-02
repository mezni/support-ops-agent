from openai import OpenAI

from support_ops.config import Settings


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