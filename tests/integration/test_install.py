def test_install(setup_no_preinstalled):
    _pkg_installer, _example_pkg, _example_instance_settings = setup_no_preinstalled
    ret = _pkg_installer.install(_example_pkg, _example_instance_settings)
    assert len(ret) == 5
