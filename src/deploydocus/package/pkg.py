import logging
from functools import wraps
from typing import Any, Dict, LiteralString, Optional, Self, Sequence

from pydantic import BaseModel, Field, model_validator

from deploydocus.package.settings import InstanceSettings
from deploydocus.package.types import (
    SUPPORTED_KINDS,
    LabelsDict,
    LabelsSelector,
    ManifestSequence,
)

logger = logging.getLogger(__name__)

DEPLOYDOCUS_DOMAIN: LiteralString = "deploydocus.io"


def autosort(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        ret: ManifestSequence = f(*args, **kwargs)
        ret.sort(
            key=lambda obj: list(SUPPORTED_KINDS).index(
                obj["kind"] if isinstance(obj, dict) else obj.kind
            )
        )
        return ret

    return wrapped


class AbstractK8sPkg(BaseModel):
    pkg_name: str = Field(default="", description="A name of this application")
    pkg_version: str = Field(
        description="Provide a version number for the application. This is independent"
        " of the individual components  of the application"
    )
    instance_settings: InstanceSettings

    @model_validator(mode="after")
    def validate_after(self: Self) -> Self:
        if not self.pkg_name:
            self.pkg_name = self.__class__.__name__
        return self

    @property
    def default_labels(self) -> LabelsDict:
        return {
            "app.kubernetes.io/name": self.pkg_name,
            "app.kubernetes.io/instance": self.instance_settings.instance_name,
            "app.kubernetes.io/version": self.instance_settings.instance_version,
            "app.kubernetes.io/managed-by": DEPLOYDOCUS_DOMAIN,
            "deploydocus-pkg": f"{self.pkg_name}-{self.pkg_version}",
        }

    @property
    def default_selectors(self) -> LabelsSelector:
        return {
            "app.kubernetes.io/name": self.pkg_name,
            "app.kubernetes.io/instance": self.instance_settings.instance_name,
            "app.kubernetes.io/managed-by": DEPLOYDOCUS_DOMAIN,
        }

    def render_namespaces(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_networkpolicys(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_resourcequotas(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_limitranges(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_poddisruptionbudgets(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_serviceaccounts(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_secrets(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_secretlists(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_configmaps(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_storageclasss(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_persistentvolumes(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_persistentvolumeclaims(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_customresourcedefinitions(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_clusterroles(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_clusterrolelists(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_clusterrolebindings(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_clusterrolebindinglists(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_roles(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_rolelists(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_rolebindings(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_rolebindinglists(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_services(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_daemonsets(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_pods(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_replicationcontrollers(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_replicasets(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_deployments(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_horizontalpodautoscalers(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_statefulsets(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_jobs(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_cronjobs(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_ingresss(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render_apiservices(self) -> Optional[Sequence[Dict[str, Any]]]:
        return None

    def render(self) -> ManifestSequence:
        """Renders the Kubernetes manifests for the application

        Returns:

        """
        manifests = [
            m
            for m in [
                self.render_namespaces(),
                self.render_networkpolicys(),
                self.render_resourcequotas(),
                self.render_limitranges(),
                self.render_poddisruptionbudgets(),
                self.render_serviceaccounts(),
                self.render_secrets(),
                self.render_secretlists(),
                self.render_configmaps(),
                self.render_storageclasss(),
                self.render_persistentvolumes(),
                self.render_persistentvolumeclaims(),
                self.render_customresourcedefinitions(),
                self.render_clusterroles(),
                self.render_clusterrolelists(),
                self.render_clusterrolebindings(),
                self.render_clusterrolebindinglists(),
                self.render_roles(),
                self.render_rolelists(),
                self.render_rolebindings(),
                self.render_rolebindinglists(),
                self.render_services(),
                self.render_daemonsets(),
                self.render_pods(),
                self.render_replicationcontrollers(),
                self.render_replicasets(),
                self.render_deployments(),
                self.render_horizontalpodautoscalers(),
                self.render_statefulsets(),
                self.render_jobs(),
                self.render_cronjobs(),
                self.render_ingresss(),
                self.render_apiservices(),
            ]
            if m
        ]

        return manifests
