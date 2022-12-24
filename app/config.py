from pydantic import BaseSettings
from functools import lru_cache


VERSION = "0.0.5"


class Settings(BaseSettings):
    app_name: str = "Polling App"
    app_version: str = VERSION
    admin_email: str = ""
    mongodb_url: str = "mongodb://localhost:27017"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
