import os
from pathlib import Path

from pydantic import AliasGenerator, alias_generators
from pydantic_settings import BaseSettings, SettingsConfigDict

from deploydocus import InstanceSettings, PkgSettings

_dir = Path(__file__).parent


class VolumeMountSettings(BaseSettings):
    model_config = SettingsConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=lambda x: alias_generators.to_pascal(x)
        )
    )

    volume_name: str
    mount_path: str


class ExampleInstanceSettings(InstanceSettings):
    model_config = SettingsConfigDict(json_file=Path(os.getcwd()) / "release.json")

    service_account_name: str
    deployment_name: str
    configmap_name: str
    args: list[str] = []
    service_name: str
    automount_sa_token: bool = True
    container_name: str
    volume_mount: VolumeMountSettings | None = None


class ExamplePkgSettings(PkgSettings):
    model_config = SettingsConfigDict(json_file=_dir / "pkg.json")
