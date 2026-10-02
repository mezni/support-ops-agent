from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_model: str = ""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _require_credentials(self) -> "Settings":
        missing = [
            name
            for name in ("openrouter_api_key", "openrouter_model")
            if not getattr(self, name).strip()
        ]
        if missing:
            env_names = ", ".join(n.upper() for n in missing)
            raise ValueError(
                f"Missing required setting(s): {env_names}. "
                f"Set them in {PROJECT_ROOT / '.env'} or as environment variables."
            )
        return self