import base64
import enum
from importlib.metadata import metadata
from pathlib import Path
from typing import (
    Any,
    Dict,
    LiteralString,
    Optional,
    Self,
    Sequence,
    cast,
    override,
)

from kubernetes.client import V1ObjectMeta
from pydantic import BaseModel, Field, SecretStr, model_validator

from ..model_partials import ConfigMap, Service, Namespace, Secret
from ... import InstanceSettings
from ..pkg import AbstractK8sPkg


class HttpDeploymentPkg(AbstractK8sPkg):
    deployment_spec: "HttpDeploymentWithService"
    create_ns: bool = Field(
        default=False,
        exclude=True,
        description="Attempt to create the namespace if not "
        "already present. Typically should not be needed.",
    )

    def render_namespaces(self) -> Optional[Sequence[Dict[str, Any]]]:
        """This expects

        Returns:

        """
        return (
            None
            if self.create_ns
            else [
                Namespace(
                    metadata=V1ObjectMeta(
                        name=self.deployment_spec.namespace, labels=self.default_labels
                    ),
                ).to_dict()
            ]
        )

    @override
    def render_secrets(self) -> Optional[Sequence[Dict[str, Any]]]:
        secrets: dict[str, dict[str, SecretStr]] = {
            f"{self.pkg_name}-configs-env": self.deployment_spec.configs_env,
            f"{self.pkg_name}-secrets-file": self.deployment_spec.secrets_file,
        }
        secrets_list = []
        for k, v in secrets.items():
            if not v:
                continue
            secret = Secret(
                immutable=True,
                type="Opaque",
                metadata=V1ObjectMeta(
                    name=k,
                    namespace=self.deployment_spec.namespace,
                    labels=self.default_labels,
                ),
                data={
                    _k: str(base64.b64encode(cast(str, _v.get_secret_value())))
                    for _k, _v in v.items()
                },
            )
            secrets_list.append(secret.to_dict())
        return None if not secrets_list else secrets_list

    @override
    def render_configmaps(self) -> Optional[Sequence[Dict[str, Any]]]:
        configs: dict[str, dict[str, str]] = {
            f"{self.pkg_name}-configs-env": self.deployment_spec.non_secrets_env,
            f"{self.pkg_name}-configs-file": self.deployment_spec.non_secrets_file,
        }
        cfgs_list = []
        for k, v in configs.items():
            if not v:
                continue
            cfg = ConfigMap(
                immutable=False,
                metadata=V1ObjectMeta(
                    name=k,
                    namespace=self.deployment_spec.namespace,
                    labels=self.default_labels,
                ),
                data={_k: str(v) for _k, _v in v.items()},
            )
            cfgs_list.append(cfg.to_dict())
        return None if not cfgs_list else cfgs_list

    @override
    def render_services(self) -> Optional[Sequence[Dict[str, Any]]]:
        return [Service(metadata)]

    @override
    def render_deployments(self) -> Optional[Sequence[Dict[str, Any]]]:
        return super().render_deployments()

    @override
    def render_ingresss(self) -> Optional[Sequence[Dict[str, Any]]]:
        return super().render_ingresss()

    @override
    def render_serviceaccounts(self) -> Optional[Sequence[Dict[str, Any]]]:
        return super().render_serviceaccounts()


class ServiceType(enum.StrEnum):
    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"


class RequestedVolumesAccessMode(enum.StrEnum):
    ReadWriteOnce = enum.auto()
    ReadOnlyMany = enum.auto()
    ReadWriteMany = enum.auto()
    ReadWriteOncePod = enum.auto()


class VolumeRequest(BaseModel):
    """Requests a Volume for"""

    name: str
    requested_storage: str
    storage_class_name: str | None = Field(
        default=None,
        description="(Recommended) the most common way to bind is by way of a storage "
        "class name. ",
    )
    match_labels: dict[str, str] | None = None
    match_volume_name: str | None = Field(
        None, description="If set, do not set any of the other matching parameters"
    )
    access_mode: RequestedVolumesAccessMode


class MountVolumeToPath(BaseModel):
    """Meant for future expansion"""

    path: Path
    named_volume: str = Field(description="")


class HttpProbes(BaseModel):
    """Represents a probe - an HTTP endpoint that the Kubernetes control plane will
    issue HTTP GET requests and if the the HTTP server inside the main pod's container
     returns a 2XX status,"""

    _default_url: str | None = None

    def __init_subclass__(cls, /, default_url=None, **kwargs):
        cls._default_url = default_url
        super().__init_subclass__(**kwargs)

    rel_url: str | None = Field(
        _default_url,
        description="The relative URL the Kubernetes will "
        "periodically issue HTTP GET requests to.",
    )
    check_freq: int = Field(
        default=10,
        description="The frequency of liveness checks"
        " (in secs). This is ignored if "
        "liveness is unset.",
    )


class HttpLivenessProbe(HttpProbes, default_url="/livez"):
    delay_first_probe: int | None = Field(
        None,
        description="If set, wait these many seconds before starting to probe the "
        "container.",
    )


class HttpReadinessProbe(HttpProbes, default_url="/readyz"):
    pass


class HttpStartupProbe(HttpProbes, default_url="/startz"):
    pass


class HttpDeploymentWithService(InstanceSettings):
    """Conventional Kubernetes Deployment with few tunable parameters. This is a
    don't-get-too-clever approach to creating a Kubernetes package that deploys a
    stateless HTTP application which by definition means if one instance of it goes
    down, it can be replaced by another running instance.
    """

    application_name: str = Field(description="(Required) The name of the application.")
    deployment_name: str | None = Field(
        None,
        description=r"(Optional) The name of the deployment. e.g. 'application-ds'. "
        r"If not provided, ",
    )
    namespace: str | None = Field(
        None,
        description=r"(Optional) Deploy the application to the given "
        r"namespace. e.g. 'application-ns' . "
        r"If the namespace does not already exist, "
        r"the deployment will fail.",
    )
    image: str = Field(
        description=r"The name of the application container image in the format "
        r"<repo>/<image_name>[:<version or sha256_tag>]. Some valid "
        r"examples are \n'gcr.io/kaniko-project/executor:v1.23.2-debug', "
        r"'gcr.io/kaniko-project/executor', "
        r"'gcr.io/kaniko-project/executor:latest', "
        r"'gcr.io/kaniko-project/executor"
        r"@sha256:9e69fd4330ec887829c780f5126dd80edc"
        r"663df6def362cd22e79bcdf00ac53f'"
    )
    http_named_ports: dict[str, int] = Field(
        description=r"The ports used by the applications. e.g. "
        r"{'http': 8080, 'grpc': 8083}. Neither port names nor their "
        r"corresponding port numbers can be repeated."
    )
    liveness_probe: HttpLivenessProbe | None = Field(
        default=None, description="(Recommended) "
    )
    readiness_probe: HttpReadinessProbe | None = None
    startup_probe: HttpStartupProbe | None = None
    replicas: int = Field(
        default=1,
        description="Number of identical, parallel instances of the "
        "application to run.",
    )

    service_name: str | None = Field(
        default=None,
        description="(optional) Can be set but it is usually automatically "
        "derived from the application_name field.",
    )
    service_named_port: dict[str, int] = Field(
        default_factory=lambda: {"http": 8080},
        description="Usually, a single named port on which the HTTP application "
        "listens to for HTTP client connections. I recommend that unless "
        "you have compelling reason to change the port name, leave the "
        "port name to 'http'. Go ahead and change the ",
    )
    service_type: str = Field(
        default="ClusterIP",
        description="Normally set to 'ClusterIP' which just "
        "assigns the  a private IP address within the "
        "cluster.",
    )
    need_ingress_svc: bool = Field(False, description="Set to True if ")

    secrets_env: Optional[dict[str, SecretStr]] = Field(default=None, frozen=True)
    secrets_file: Optional[dict[str, SecretStr]] = Field(default=None, frozen=True)
    non_secrets_env: Optional[dict[str, str]] = Field(default=None, frozen=True)
    non_secrets_file: Optional[dict[str, str]] = Field(default=None, frozen=True)

    pkg_version: LiteralString = Field(
        default="v1",
        frozen=True,
        description="This controls the version number " "of the pkg",
        validate_default=True,
    )

    @model_validator(mode="after")
    def sset_by_default(self) -> Self:
        return self

    def k8spkg(self) -> AbstractK8sPkg:
        return HttpDeploymentPkg(
            pkg_name=self.application_name,
            pkg_version=self.pkg_version,
            instance_settings=InstanceSettings(
                instance_name=self.deployment_name,
                instance_version=self.pkg_version,
                instance_namespace=self.instance_namespace,
            ),
            deployment_spec=self,
        )


class K8sService(BaseModel):
    service_port: int
    container_port: int | None = None


def repeated_elems[T](elems: list[T]) -> list[T]:
    uniq_elems = set(elems)
    rep_elems = [x for x in elems if not (x in uniq_elems)]
    return rep_elems
