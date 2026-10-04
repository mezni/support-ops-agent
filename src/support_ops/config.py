from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "support-ops-agent"
    environment: str = "dev"
    log_level: str = "INFO"

    openrouter_api_key: str
    openrouter_model: str

    database_path: str = "data/support_ops.db"

    max_agent_iterations: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
