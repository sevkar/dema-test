from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_DSN: str
    PREFECT_API_URL: str | None = None
    RAW_DATA_PATH: str = "data/raw"


settings = Settings()
