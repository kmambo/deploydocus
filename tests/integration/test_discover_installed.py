import logging

from example_app_pkg import ExamplePkg
from kubernetes.client.rest import logger as krlogger

from deploydocus.appstate import PkgInstaller
from deploydocus.package.types import K8sModelSequence

krlogger.setLevel(logging.WARN)


def test_discover_installed(
    setup_preinstalled: tuple[PkgInstaller, ExamplePkg, K8sModelSequence]
):
    installer, example_pkg, installed_components = setup_preinstalled
    discovered_components = installer.find_current_app_installations(example_pkg)
    ic_kn = [(i.kind, i.metadata.name) for i in installed_components]
    dc_kn = [(i.kind, i.metadata.name) for i in discovered_components]
    equals = list(map(lambda x: x in dc_kn, ic_kn))
    assert all(equals), f"{ic_kn=}, {dc_kn=}, {equals=}"
