from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql+psycopg2://nqs:localdev@localhost:5432/nqs"
    gemini_api_key: str = ""
    environment: str = "development"


settings = Settings()