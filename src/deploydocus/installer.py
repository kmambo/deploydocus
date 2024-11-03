import tempfile

from .appstate.helm3 import HelmChart
from .appstate.kustomize import Kustomization

type LegacyTools = HelmChart | Kustomization


class ClusterContext:
    """Represents the Kubernetes cluster on which to operate and any authentication
    needed to .
    May well be non-cluster admin context but the presumption is that if the installer
    is using this context to perform an operation such as install a helm chart, then
    it has the necessary permissions to be able to complete the operation.
    """

    ...


class ApplicationInstaller:
    def __init__(self, ctx: ClusterContext):
        self.ctx = ctx

    def apply(self, pkg: LegacyTools):
        """renders and applies an assembled package to the cluster using the
        cluster context.
        """
        with tempfile.NamedTemporaryFile() as ntf:
            with tempfile.TemporaryDirectory() as td:
                resources_raw: str = pkg.render(td)
            ntf.write(resources_raw)  # type: ignore[call-overload]
