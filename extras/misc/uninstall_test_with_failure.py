import logging
from typing import Any, override

from example_app_pkg import ExampleInstanceSettings, ExamplePkg

from deploydocus import PkgInstaller
from deploydocus.installer.errors import InstallError
from deploydocus.installer.types import ManifestDict

logger = logging.getLogger(__name__)


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


if __name__ == "__main__":
    i = ExampleInstanceSettings()
    bad_example_pkg = BadExamplePackage()
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    install_tracker: list[ManifestDict] = []
    try:
        pkg_installer.install(bad_example_pkg, i, install_tracker)
        logger.info(install_tracker)
    except InstallError:
        logger.error("Installation Failure. Reversing install of installed components")
        uninstalled = pkg_installer.revert_install(
            install_tracker, namespace=i.instance_namespace
        )
