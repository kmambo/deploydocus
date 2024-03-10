from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    chart_name: str
    chart_tag: str
    app_instance: str
    app_version: str
    instance_name: str
    image_name_with_tag: str | None
    container_name: str | None

    @computed_field  # type: ignore[misc]
    @property
    def sa_account_name(self) -> str:
        return f"{self.instance_name}-{self.chart_name}"
