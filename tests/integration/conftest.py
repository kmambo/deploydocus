import json
import pathlib
from typing import Any, Generator, override

import pytest
from example_app_pkg import ExampleInstanceSettings, ExamplePkg
from plumbum import local

from deploydocus import InstanceSettings
from deploydocus.installer import PkgInstaller
from deploydocus.types import K8sModel, K8sModelSequence


@pytest.fixture
def example_instance_settings() -> ExampleInstanceSettings:
    json_file = pathlib.Path(__file__).parent / "release.json"
    with open(json_file, "rt") as f:
        i = ExampleInstanceSettings(**json.load(f))
    return i


def _uninstall(namespace, service, deployment, configmap):
    _kdel = local["kubectl"]
    _kdel("delete", "service", service, "-n", namespace, retcode=None)
    _kdel("delete", "deployment", deployment, "-n", namespace, retcode=None)
    _kdel("delete", "configmap", configmap, "-n", namespace, retcode=None)
    _kdel("delete", "ns", namespace, retcode=None)


@pytest.fixture
def example_pkg(example_instance_settings) -> Generator[ExamplePkg, None, None]:
    ret = ExamplePkg(example_instance_settings)
    yield ret


@pytest.fixture
def bad_example_pkg(
    example_instance_settings: ExampleInstanceSettings,
) -> Generator[ExamplePkg, None, None]:
    class BadExamplePackage(ExamplePkg):

        def __init__(
            self,
            instance: InstanceSettings,
            *,
            pkg_version: str | None = None,
            pkg_name: str | None = None,
        ):
            super().__init__(instance, pkg_version=pkg_version, pkg_name=pkg_name)

        @override
        def render_default_deployment(self) -> dict[str, Any]:
            obj_dict = super().render_default_deployment()
            obj_dict["spec"]["selector"]["matchLabels"][
                "app.kubernetes.io/name"
            ] = "hello-world"
            return obj_dict

    ret = BadExamplePackage(example_instance_settings)
    yield ret


@pytest.fixture
def setup_preinstalled(
    example_pkg: ExamplePkg,
) -> Generator[tuple[PkgInstaller, ExamplePkg, K8sModelSequence], None, None]:
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    components: list[K8sModel] = []
    try:
        pkg_installer.install(example_pkg, installed=components)
        yield pkg_installer, example_pkg, components
    finally:
        _uninstall(
            namespace=example_pkg.instance_settings.instance_namespace,
            service=example_pkg.render_default_service()["metadata"]["name"],
            deployment=example_pkg.render_default_deployment()["metadata"]["name"],
            configmap=example_pkg.render_default_configmap()["metadata"]["name"],
        )


@pytest.fixture
def setup_no_preinstalled(
    example_pkg: ExamplePkg,
) -> Generator[tuple[PkgInstaller, ExamplePkg], None, None]:
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    yield pkg_installer, example_pkg,
    _uninstall(
        namespace=example_pkg.instance_settings.instance_namespace,
        service=example_pkg.render_default_service()["metadata"]["name"],
        deployment=example_pkg.render_default_deployment()["metadata"]["name"],
        configmap=example_pkg.render_default_configmap()["metadata"]["name"],
    )
