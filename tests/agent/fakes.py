"""Test fakes for the support-ops agent."""

# Pre-defined fake decisions
_agent_decision = None


def set_fake_decision(decision):
    """Set the default fake decision for FakeLLM."""
    global _agent_decision
    _agent_decision = decision


def get_fake_decision():
    """Get the default fake decision."""
    if _agent_decision is None:
        _agent_decision = AgentDecision(
            action="create_ticket",
            reason="The issue requires investigation.",
            tool_name="create_ticket",
            tool_arguments={"customer_id": "C-001", "subject": "test", "description": "test"},
        )
    return _agent_decision


class AgentDecision:
    """Fake agent decision."""

    def __init__(
        self,
        action: str,
        reason: str,
        tool_name: str | None = None,
        tool_arguments: dict | None = None,
    ):
        self.action = action
        self.reason = reason
        self.tool_name = tool_name
        self.tool_arguments = tool_arguments or {}


class AgentState:
    """Fake agent state."""

    def __init__(
        self,
        ticket: object,
        status: str = "running",
        iteration: int = 0,
        max_iterations: int = 5,
        tool_calls: list | None = None,
        final_response: str | None = None,
        error: str | None = None,
    ):
        self.ticket = ticket
        self.status = status
        self.iteration = iteration
        self.max_iterations = max_iterations
        self.tool_calls = tool_calls or []
        self.final_response = final_response
        self.error = error


class FakeLLM:
    """Fake LLM that returns a predetermined decision."""

    def __init__(self, decision=None):
        self.decision = decision or get_fake_decision()

    def structured(self, message, output_model):
        return self.decision


class ScriptedLLM:
    """Returns a queued decision per call and records every prompt."""

    def __init__(self, decisions):
        self.decisions = list(decisions)
        self.prompts = []

    def structured(self, message, output_model):
        self.prompts.append(message)

        if not self.decisions:
            raise AssertionError("ScriptedLLM ran out of decisions.")

        return self.decisions.pop(0)