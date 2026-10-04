from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    total: int = 0
    passed: int = 0

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0

        return self.passed / self.total


def calculate_accuracy(
    expected: list,
    actual: list,
) -> float:
    if not expected:
        return 0.0

    matches = sum(
        1
        for expected_value, actual_value in zip(expected, actual)
        if expected_value == actual_value
    )

    return matches / len(expected)
