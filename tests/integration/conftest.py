import json
import pathlib
from typing import Any, override

import pytest
from example_app_pkg import ExampleInstanceSettings, ExamplePkg

from deploydocus import PkgInstaller


@pytest.fixture
def example_pkg():
    ret = ExamplePkg()
    yield ret


@pytest.fixture
def example_instance_settings():
    json_file = pathlib.Path(__file__).parent / "release.json"
    with open(json_file, "rt") as f:
        i = ExampleInstanceSettings(**json.load(f))
    yield i


@pytest.fixture
def bad_example_pkg():
    class BadExamplePackage(ExamplePkg):

        @override
        def render_default_deployment(
            self, instance_settings: ExampleInstanceSettings
        ) -> dict[str, Any]:
            obj_dict = super().render_default_deployment(instance_settings)
            obj_dict["spec"]["selector"]["matchLabels"][
                "app.kubernetes.io/name"
            ] = "hello-world"
            return obj_dict

    ret = BadExamplePackage()
    yield ret


@pytest.fixture
def setup_preinstalled(example_pkg, example_instance_settings):
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    pkg_installer.install(example_pkg, example_instance_settings)
    yield pkg_installer, example_pkg, example_instance_settings
    pkg_installer.uninstall(example_pkg, example_instance_settings)


@pytest.fixture
def setup_no_preinstalled(example_pkg, example_instance_settings):
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    yield pkg_installer, example_pkg, example_instance_settings
    pkg_installer.uninstall(example_pkg, example_instance_settings)
