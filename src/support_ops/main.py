import uvicorn

from support_ops.api.app import create_app
from support_ops.config import Settings
from support_ops.container import create_application


def main() -> None:
    settings = Settings()
    application = create_application(settings)
    app = create_app(application)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
