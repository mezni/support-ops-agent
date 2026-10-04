from support_ops.config import Settings


def test_default_configuration(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    settings = Settings()

    assert settings.environment == "dev"
    assert settings.log_level == "INFO"
    assert settings.database_path == "data/support_ops.db"
    assert settings.max_agent_iterations == 5


def test_environment_overrides(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("MAX_AGENT_ITERATIONS", "10")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.max_agent_iterations == 10
