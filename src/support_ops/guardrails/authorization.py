class AuthorizationService:
    """Service for authorizing agent actions."""

    def authorize(self, action: str) -> bool:
        """Check if the given action is authorized."""
        # In a production system, this would check permissions,
        # user roles, etc.
        # For now, all actions are authorized.
        return True
