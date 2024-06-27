import json
import pathlib
from tempfile import NamedTemporaryFile
from typing import Any, Generator, override

import pytest
import yaml
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


def _uninstall_test_util(namespace: str, service: str, deployment: str, configmap: str):
    """Utility function used during testing to delete installed components

    Args:
        namespace: The name of the namespace to be deleted
        service: The name of the service to be deleted
        deployment: The name of the deployment to be deleted
        configmap: The name of the configmap to be deleted

    Returns:
        None
    """
    kubectl = local["kubectl"]
    kubectl("delete", "service", service, "-n", namespace, retcode=None)
    kubectl("delete", "deployment", deployment, "-n", namespace, retcode=None)
    kubectl("delete", "configmap", configmap, "-n", namespace, retcode=None)
    kubectl("delete", "ns", namespace, retcode=None)


def _install_test_util(rendered: list[dict[str, Any]]):
    """Utility function used during testing to apply a rendered package

    Args:
        rendered: The rendered package

    Returns:
        None
    """
    kubectl = local["kubectl"]  # find kubectl
    with NamedTemporaryFile("wt") as f:
        yaml.safe_dump_all(rendered, f)
        f.flush()
        kubectl("apply", "-f", f.name, retcode=None)


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

    bad_example_pkg = BadExamplePackage(example_instance_settings)
    yield bad_example_pkg
    _uninstall_test_util(
        namespace=bad_example_pkg.instance_settings.instance_namespace,
        service=bad_example_pkg.render_default_service()["metadata"]["name"],
        deployment=bad_example_pkg.render_default_deployment()["metadata"]["name"],
        configmap=bad_example_pkg.render_default_configmap()["metadata"]["name"],
    )


@pytest.fixture
def setup_preinstalled(
    example_pkg: ExamplePkg,
) -> Generator[tuple[PkgInstaller, ExamplePkg, K8sModelSequence], None, None]:
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    components: list[K8sModel] = []
    try:
        rendered = example_pkg.render()
        _install_test_util(rendered)
        yield pkg_installer, example_pkg, components
    finally:
        _uninstall_test_util(
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
    _uninstall_test_util(
        namespace=example_pkg.instance_settings.instance_namespace,
        service=example_pkg.render_default_service()["metadata"]["name"],
        deployment=example_pkg.render_default_deployment()["metadata"]["name"],
        configmap=example_pkg.render_default_configmap()["metadata"]["name"],
    )
