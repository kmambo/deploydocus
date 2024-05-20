def test_uninstall(setup_preinstalled):
    _pkg_installer, _example_pkg, example_inst_settings = setup_preinstalled
    ret = _pkg_installer.uninstall(_example_pkg, example_inst_settings)
    print(ret)
