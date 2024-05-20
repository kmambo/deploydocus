import logging

from deploydocus import PkgInstaller
from deploydocus.installer.errors import InstallError
from deploydocus.installer.types import ManifestDict

logger = logging.getLogger(__name__)


def test_atomic_uninstall_upon_install_failure(
    bad_example_pkg, example_instance_settings
):
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    install_tracker: list[ManifestDict] = []
    try:
        pkg_installer.install(
            bad_example_pkg, example_instance_settings, install_tracker
        )
        logger.info(install_tracker)
    except InstallError:
        logger.error("Installation Failure. Reversing install of installed components")
        uninstalled = pkg_installer.revert_install(
            install_tracker, namespace=example_instance_settings.instance_namespace
        )
        assert len(uninstalled) == 3
