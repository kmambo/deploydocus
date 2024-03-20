from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        json_file=["chart.json", "release.json"],
        json_file_encoding="utf-8",
    )

    chart_name: str
    chart_version: str
    release_name: str
    app_version: str
    image_name_with_tag: str | None
    app_namespace: str
    dry_run: bool = False
