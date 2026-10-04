from support_ops.evaluation.cases import EVALUATION_CASES, EvaluationCase
from support_ops.evaluation.metrics import EvaluationMetrics, calculate_accuracy


def test_evaluation_cases_non_empty() -> None:
    """Verify the evaluation cases dataset is populated."""
    assert len(EVALUATION_CASES) > 0


def test_evaluation_case_fields() -> None:
    """Verify EvaluationCase has the expected fields."""
    case = EVALUATION_CASES[0]
    assert case.name == "duplicate_billing"
    assert case.customer_id == "C-001"
    assert case.subject == "Charged twice"
    assert case.expected_action is not None


def test_metrics_total() -> None:
    """Verify EvaluationMetrics tracks total count."""
    metrics = EvaluationMetrics(total=4)
    assert metrics.total == 4


def test_metrics_accuracy() -> None:
    """Verify EvaluationMetrics accuracy property."""
    metrics = EvaluationMetrics(total=4, passed=2)
    assert metrics.accuracy == 0.5


def test_calculate_accuracy_perfect() -> None:
    """Verify calculate_accuracy returns 1.0 for perfect match."""
    assert (
        calculate_accuracy(
            ["a", "b", "c"],
            ["a", "b", "c"],
        )
        == 1.0
    )


def test_calculate_accuracy_partial() -> None:
    """Verify calculate_accuracy returns correct fraction."""
    assert (
        calculate_accuracy(
            ["a", "b", "c"],
            ["a", "x", "c"],
        )
        == 2 / 3
    )


def test_calculate_accuracy_empty() -> None:
    """Verify calculate_accuracy returns 0.0 for empty lists."""
    assert calculate_accuracy([], []) == 0.0
