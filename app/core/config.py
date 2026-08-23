from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    ai_provider: str = "openai_compatible"
    ai_base_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "llama-3.1-8b-instant"
    ai_api_key: str = ""

    market_data_provider: str = "demo"
    market_data_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
