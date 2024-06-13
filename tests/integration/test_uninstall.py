from example_app_pkg import ExamplePkg

from deploydocus.installer import PkgInstaller
from deploydocus.types import ManifestSequence


def test_uninstall(
    setup_preinstalled: tuple[PkgInstaller, ExamplePkg, ManifestSequence]
):
    _pkg_installer, _example_pkg, installed = setup_preinstalled
    ret = _pkg_installer.uninstall(_example_pkg)
    assert len(ret) == len(installed)
    ret1 = [(r.metadata.name, getattr(r.metadata, "namespace")) for r in ret]
    installed1 = [
        (r.metadata.name, getattr(r.metadata, "namespace")) for r in installed
    ]
    assert all([r in installed1 for r in ret1])
