from .models import ConversationMessage


class ShortTermMemory:
    def __init__(self) -> None:
        self._messages: list[ConversationMessage] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append(
            ConversationMessage(
                role=role,
                content=content,
            )
        )

    def get_messages(self) -> list[ConversationMessage]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()
