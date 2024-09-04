import logging

import pytest
from kubernetes.client import ApiException

from deploydocus.appstate import PkgInstaller
from deploydocus.package.types import ManifestDict

logger = logging.getLogger(__name__)


def test_atomic_uninstall_upon_install_failure(
    bad_example_pkg, example_instance_settings
):
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    install_tracker: list[ManifestDict] = []
    with pytest.raises(ApiException) as ae:
        pkg_installer.install(bad_example_pkg, install_tracker)
    assert ae.value.status == 422
    uninstalled = pkg_installer.revert_install(
        install_tracker, namespace=example_instance_settings.instance_namespace
    )
    assert len(uninstalled) == len(install_tracker)
