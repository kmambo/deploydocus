from typing import Any

from kubernetes.client import (  # type: ignore
    V1Container,
    V1Deployment,
    V1DeploymentSpec,
    V1DeploymentStatus,
    V1HorizontalPodAutoscaler,
    V1ObjectMeta,
    V1PodSpec,
    V1PodTemplateSpec,
    V1SecurityContext,
    V1Service,
    V1ServiceAccount,
    V1ServicePort,
    V1ServiceSpec,
)

from deploydocus.settings import DefaultSettings

_create_default_components = [
    "deployment",
    "service",
    "hpa",
    "ingress",
    "service_account",
]


class DefaultChart:

    def __init__(
        self,
        settings: DefaultSettings,
    ):
        """

        Args:
            settings:
        """
        self.settings = settings

    def create_default_deployment(
        self,
        *,
        metadata: V1ObjectMeta | None = None,
        status: V1DeploymentStatus | None = None,
        pod_template_spec: V1PodTemplateSpec | None = None,
        image_name_with_tag: str | None = None,
        replicas: int = 1,
        security_context=None,
    ) -> V1Deployment:
        selector = {
            "app.kubernetes.io/name": self.chart_name,
            "app.kubernetes.io/instance": self.app_instance,
            "app.kubernetes.io/version": self.chart_tag,
            "app.kubernetes.io/managed-by": "deploydocus.io",
        }
        metadata = metadata or V1ObjectMeta(
            name=f"{self.app_instance}-{self.chart_name}", labels=self.labels
        )
        pod_spec = V1PodSpec(
            automount_service_account_token=True,
            containers=[
                V1Container(
                    image=image_name_with_tag or self.settings.image_name_with_tag,
                    name=self.settings.container_name or self.app_instance,
                    security_context=security_context,
                ),
            ],
        )
        pod_template_spec = pod_template_spec or V1PodTemplateSpec(
            metadata=metadata, spec=pod_spec
        )
        security_context = security_context or V1SecurityContext()
        # pod_template_spec.spec.containers = [
        #     V1Container(image=image_name_with_tag or self.settings.image_name_with_tag,
        #                 security_context=security_context)
        # ]
        spec = V1DeploymentSpec(
            selector=selector,
            template=pod_template_spec,
            replicas=replicas,
        )
        status = status or V1DeploymentStatus()

        deployment: V1Deployment = V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=metadata,
            spec=spec,
            status=status,
        )

        return deployment

    def create_default_service(
        self,
        port=80,
        port_name="http",
        protocol="TCP",
    ) -> V1Service:
        metadata = V1ObjectMeta(
            name=f"{self.app_instance}-{self.chart_name}", labels=self.labels
        )
        svc_spec = V1ServiceSpec(
            type="ClusterIP",
            selector=self.selectors,
            ports=[V1ServicePort(name=port_name, port=port, protocol=protocol)],
        )
        svc = V1Service(
            api_version="v1", kind="Service", metadata=metadata, spec=svc_spec
        )
        return svc

    def create_default_sa(self, sa_name=None) -> V1ServiceAccount:
        sa_name = sa_name or self.settings.sa_account_name

        metadata = V1ObjectMeta(name=sa_name, labels=self.labels)
        return V1ServiceAccount(
            api_version="v1",
            kind="ServiceAccount",
            metadata=metadata,
            automount_service_account_token=True,
        )

    def create_default_hpa(self) -> V1HorizontalPodAutoscaler: ...

    @property
    def labels(self):
        return {
            "app.kubernetes.io/name": f"{self.chart_name}",
            "app.kubernetes.io/instance": f"{self.app_instance}",
            "app.kubernetes.io/version": f"{self.app_version}",
            "app.kubernetes.io/managed-by": "deploydocus.io",
        }

    @property
    def chart_tag(self) -> str:
        return f"{self.settings.chart_tag}"

    @property
    def chart_name(self) -> str:
        return f"{self.settings.chart_name}"

    @property
    def chart_fullname(self) -> str:
        return f"{self.chart_name}-{self.chart_tag}"

    @property
    def app_instance(self) -> str:
        return f"{self.settings.app_instance}"

    @property
    def app_version(self) -> str:
        return f"{self.settings.app_version}"

    @property
    def selectors(self) -> dict[str, str]:
        return {
            "app.kubernetes.io/name": f"{self.chart_name}",
            "app.kubernetes.io/instance": f"{self.app_instance}",
        }
