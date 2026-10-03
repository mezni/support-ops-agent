from support_ops.memory.manager import MemoryManager


def test_short_term_memory():
    memory = MemoryManager()

    memory.remember_message(
        "user",
        "I was charged twice.",
    )

    messages = memory.get_conversation()

    assert len(messages) == 1
    assert messages[0].role == "user"
    assert messages[0].content == "I was charged twice."


def test_customer_memory():
    memory = MemoryManager()

    memory.remember_fact(
        "C-100",
        "plan",
        "enterprise",
    )

    customer = memory.get_customer("C-100")

    assert customer.facts["plan"] == "enterprise"


def test_previous_tickets():
    memory = MemoryManager()

    memory.remember_ticket(
        "C-100",
        "T-001",
    )

    customer = memory.get_customer("C-100")

    assert "T-001" in customer.previous_tickets
