from .models import CustomerMemory


class LongTermMemory:
    def __init__(self) -> None:
        self._customers: dict[str, CustomerMemory] = {}

    def get(self, customer_id: str) -> CustomerMemory:
        if customer_id not in self._customers:
            self._customers[customer_id] = CustomerMemory(customer_id=customer_id)

        return self._customers[customer_id]

    def save(self, memory: CustomerMemory) -> None:
        self._customers[memory.customer_id] = memory

    def add_ticket(
        self,
        customer_id: str,
        ticket_id: str,
    ) -> None:
        memory = self.get(customer_id)

        if ticket_id not in memory.previous_tickets:
            memory.previous_tickets.append(ticket_id)

    def add_fact(
        self,
        customer_id: str,
        key: str,
        value: str,
    ) -> None:
        memory = self.get(customer_id)
        memory.facts[key] = value

    def add_preference(
        self,
        customer_id: str,
        key: str,
        value: str,
    ) -> None:
        memory = self.get(customer_id)
        memory.preferences[key] = value
