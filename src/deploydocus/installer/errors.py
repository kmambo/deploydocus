from kubernetes.utils import FailToCreateError


class InstallError(Exception):
    def __init__(self, exc: FailToCreateError, *args):
        self.exc = exc
        super().__init__(*args)

    def __repr__(self) -> str:
        ret = repr(self.exc) + "\n" + super().__repr__()
        return ret


class KubeConfigError(Exception):
    pass
