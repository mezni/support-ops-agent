from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
)


class ScriptedLLM:
    """
    Returns a queued decision per call and records every prompt.
    """

    def __init__(
        self,
        decisions: list[AgentDecision],
    ) -> None:
        self.decisions = decisions
        self.prompts: list[str] = []

    def structured(
        self,
        message: str,
        output_model: type,
    ) -> AgentDecision:
        self.prompts.append(message)

        if not self.decisions:
            raise AssertionError("ScriptedLLM ran out of decisions.")

        return self.decisions.pop(0)


class FakeLLM(ScriptedLLM):
    """
    Always returns the same decision, whatever the prompt.

    The default decision asks for create_ticket, so a run exhausts
    max_iterations rather than completing.
    """

    def __init__(
        self,
        decision: AgentDecision | None = None,
    ) -> None:
        super().__init__([])

        self.decision = decision or AgentDecision(
            action=AgentAction.CREATE_TICKET,
            reason="The issue requires investigation.",
            tool_name="create_ticket",
            tool_arguments={
                "customer_id": "C-001",
                "subject": "Cannot access account",
                "description": "My account is locked.",
            },
        )

    def structured(
        self,
        message: str,
        output_model: type,
    ) -> AgentDecision:
        self.prompts.append(message)

        return self.decision
