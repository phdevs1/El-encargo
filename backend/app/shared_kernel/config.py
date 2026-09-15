from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "waitlist_app"
    mysql_password: str = "change-me"
    mysql_database: str = "waitlist"

    # NoDecode: pydantic-settings would otherwise try to JSON-decode a
    # list[str] env var before our validator ever runs — this defers
    # parsing to _split_csv below, so a plain comma-separated string works.
    cors_allowed_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_csv(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


settings = Settings()
