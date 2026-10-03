from .long_term import LongTermMemory
from .models import CustomerMemory
from .short_term import ShortTermMemory


class MemoryManager:
    def __init__(self) -> None:
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

    def remember_message(
        self,
        role: str,
        content: str,
    ) -> None:
        self.short_term.add(role, content)

    def get_conversation(self):
        return self.short_term.get_messages()

    def get_customer(
        self,
        customer_id: str,
    ) -> CustomerMemory:
        return self.long_term.get(customer_id)

    def remember_fact(
        self,
        customer_id: str,
        key: str,
        value: str,
    ) -> None:
        self.long_term.add_fact(
            customer_id,
            key,
            value,
        )

    def remember_ticket(
        self,
        customer_id: str,
        ticket_id: str,
    ) -> None:
        self.long_term.add_ticket(
            customer_id,
            ticket_id,
        )
