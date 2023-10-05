from pydantic import EmailStr, Field
from functools import lru_cache
import importlib.metadata
import unipoll_api.__version__ as version_file
from pydantic_settings import BaseSettings, SettingsConfigDict


try:
    VERSION = importlib.metadata.version('unipoll-api')
except importlib.metadata.PackageNotFoundError:
    VERSION = version_file.version


class Settings(BaseSettings):  # type: ignore
    app_name: str = Field(default="University Polling API",
                          title="App Name", description="The name of the API.")
    app_version: str = Field(default=VERSION, title="App Version", description="The version of the API.")
    app_description: str = Field(default=("An Open Source API for creating surveys and polls "
                                          "to assist in university research."),
                                 title="App Description", description="A description of the API.")
    admin_email: EmailStr = Field(default="admin@example.com",
                                  title="Admin Email", description="The email address of the API administrator.")
    mongodb_url: str = Field(default="mongodb://localhost:27017",
                             title="MongoDB URL", description="The URL of the MongoDB database.")
    secrete_key: str = Field(default="secret", title="Secrete Key", description="The secrete key of the API.")
    origins: str = "*"
    host: str = "0.0.0.0"
    port: int = 9000
    reload: bool = True
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
