from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    lms_api_base_url: str = ""
    lms_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""

    model_config = SettingsConfigDict(
        env_file="../.env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()
