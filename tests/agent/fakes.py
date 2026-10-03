from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
)


class FakeLLM:
    def structured(
        self,
        message: str,
        output_model: type,
    ):
        return AgentDecision(
            action=AgentAction.CREATE_TICKET,
            reason="The issue requires investigation.",
        )
