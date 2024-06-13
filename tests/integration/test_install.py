from example_app_pkg import ExamplePkg

from deploydocus.installer import PkgInstaller


def test_install(setup_no_preinstalled: tuple[PkgInstaller, ExamplePkg]):
    (
        _pkg_installer,
        _example_pkg,
    ) = setup_no_preinstalled
    ret = _pkg_installer.install(_example_pkg)
    assert len(ret) == 5
    assert not isinstance(ret[0], list)
