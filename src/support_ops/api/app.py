from fastapi import FastAPI

from support_ops.api.routes import create_router
from support_ops.application.service import SupportApplication


def create_app(application: SupportApplication) -> FastAPI:
    app = FastAPI(title="Support Ops Agent")

    app.include_router(create_router(application))

    return app
