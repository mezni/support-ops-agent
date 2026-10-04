from support_ops.domain.ticket import IncomingTicket

from .cases import EvaluationCase
from .metrics import EvaluationMetrics


class EvaluationRunner:
    def __init__(self, agent) -> None:
        self.agent = agent

    def run(
        self,
        cases: list[EvaluationCase],
    ) -> EvaluationMetrics:

        metrics = EvaluationMetrics(total=len(cases))

        for case in cases:
            ticket = IncomingTicket(
                id=case.name,
                customer_id=case.customer_id,
                subject=case.subject,
                description=case.description,
            )

            state = self.agent.run(ticket)

            if case.expected_action is not None and state.status.value == "completed":
                metrics.passed += 1

        return metrics
