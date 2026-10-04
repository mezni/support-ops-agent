from support_ops.application.service import SupportApplication


def create_router(application: SupportApplication):
    """Create the FastAPI router for the support ops application."""
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/health")
    async def health_check():
        return {"status": "ok"}

    return router
