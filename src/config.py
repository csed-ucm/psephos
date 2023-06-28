from pydantic import BaseSettings
from functools import lru_cache


VERSION = "0.0.7"


class Settings(BaseSettings):
    app_name: str = "University Polling API"
    app_version: str = VERSION
    app_description: str = "An Open Source API for creating surveys and polls to assist in university research."
    admin_email: str = ""
    mongodb_url: str = "mongodb://localhost:27017"
    secrete_key: str = "secret"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
