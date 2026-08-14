from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://nqs:localdev@localhost:5432/nqs"
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()        