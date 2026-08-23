from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    ai_provider: str = "openai_compatible"
    ai_base_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "openai/gpt-oss-20b"
    ai_api_key: str = ""

    market_data_provider: str = "demo"
    market_data_api_key: str = ""
    market_data_base_url: str = "https://pro-api.coinmarketcap.com"

    execution_log_enabled: bool = True
    execution_log_dir: str = "execution_logs"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
