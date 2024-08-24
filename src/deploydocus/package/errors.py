from deploydocus.package.types import K8sModel


class KubeConfigError(Exception):
    pass


class PkgAlreadyInstalled(Exception):
    components_found: list[K8sModel]

    def __init__(self, components_found: list[K8sModel], *args):
        self.components_found = [c for c in components_found]
        super().__init__(f"{components_found}", *args)
