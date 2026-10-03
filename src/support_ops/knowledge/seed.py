from support_ops.knowledge.document import KnowledgeDocument


def default_documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            id="KB-001",
            title="Password Reset",
            category="account",
            content=(
                "Customers can reset their password from the "
                "login page by selecting 'Forgot password'. "
                "A password reset email will be sent to the "
                "customer's registered email address."
            ),
        ),
        KnowledgeDocument(
            id="KB-002",
            title="Duplicate Billing Charge",
            category="billing",
            content=(
                "If a customer believes they were charged twice, "
                "support should verify the billing transaction "
                "before issuing a refund."
            ),
        ),
        KnowledgeDocument(
            id="KB-003",
            title="Account Locked",
            category="account",
            content=(
                "Accounts can become temporarily locked after "
                "multiple unsuccessful login attempts."
            ),
        ),
        KnowledgeDocument(
            id="KB-004",
            title="Refund Policy",
            category="billing",
            content=(
                "Refund requests should be reviewed against the "
                "company refund policy before approval."
            ),
        ),
    ]