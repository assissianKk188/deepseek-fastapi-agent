from deepseek_fastapi_agent.config import Settings


def test_settings_has_deepseek_defaults() -> None:
    settings = Settings(deepseek_api_key="test-key")

    assert settings.deepseek_model == "deepseek-v4-flash"
    assert settings.deepseek_base_url == "https://api.deepseek.com"

