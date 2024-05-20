from kubernetes.utils import FailToCreateError

from deploydocus.installer.types import ManifestDict


class InstallError(Exception):
    def __init__(self, exc: FailToCreateError, component: ManifestDict, *args):
        self.exc = exc
        self.component = component
        super().__init__(*args)

    def __repr__(self) -> str:
        ret = repr(self.exc) + "\n" + super().__repr__()
        return ret


class KubeConfigError(Exception):
    pass
