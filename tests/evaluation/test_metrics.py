from support_ops.evaluation.metrics import calculate_accuracy


def test_perfect_accuracy() -> None:
    assert (
        calculate_accuracy(
            ["a", "b", "c"],
            ["a", "b", "c"],
        )
        == 1.0
    )


def test_partial_accuracy() -> None:
    assert (
        calculate_accuracy(
            ["a", "b", "c"],
            ["a", "x", "c"],
        )
        == 2 / 3
    )


def test_empty_accuracy() -> None:
    assert (
        calculate_accuracy(
            [],
            [],
        )
        == 0.0
    )
