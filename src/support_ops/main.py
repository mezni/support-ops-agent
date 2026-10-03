from support_ops.config import Settings
from support_ops.llm import LLMClient


def main() -> None:
    settings = Settings()
    llm = LLMClient(settings)

    response = llm.chat(
        "You are a customer support assistant. "
        "Explain briefly what a support ticket is."
    )

    print(response)


if __name__ == "__main__":
    main()
