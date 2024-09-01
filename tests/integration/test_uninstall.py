from typing import Sequence

from deploydocus.appstate import PkgInstaller
from deploydocus.package.types import K8sModel, K8sModelSequence

from .example_app_pkg import ExamplePkg


def test_uninstall(
    setup_preinstalled: tuple[PkgInstaller, ExamplePkg, K8sModelSequence]
):
    _pkg_installer, _example_pkg, installed = setup_preinstalled
    ret: Sequence[K8sModel] = _pkg_installer.uninstall(_example_pkg)
    assert len(ret) == len(installed)
    ret1 = [(r.metadata.name, getattr(r.metadata, "namespace")) for r in ret]
    installed1 = [
        (r.metadata.name, getattr(r.metadata, "namespace")) for r in installed
    ]
    assert all([r in installed1 for r in ret1])
