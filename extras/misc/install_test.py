from example_app_pkg import ExampleInstanceSettings, ExamplePkg

from deploydocus import PkgInstaller

if __name__ == "__main__":
    i = ExampleInstanceSettings()
    example_pkg = ExamplePkg()
    pkg_installer = PkgInstaller(context="kind-deploydocus")
    ret = pkg_installer.install(example_pkg, i)
    print(ret)
