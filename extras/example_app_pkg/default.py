import logging
from typing import Any, cast

from deploydocus.logging.configure import configure_logging
from deploydocus.package.pkg import AbstractK8sPkg
from deploydocus.settings import InstanceSettings
from deploydocus.types import ManifestSequence

from .settings import ExampleInstanceSettings

configure_logging()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExamplePkg(AbstractK8sPkg):

    def __init__(
        self,
        instance: InstanceSettings,
        *,
        pkg_version: str | None = None,
        pkg_name: str | None = None,
    ):
        assert isinstance(instance, ExampleInstanceSettings), (
            f"parameter instance should be of type ExampleInstanceSettings. Instead"
            f" it is of type {type(instance)}"
        )
        super().__init__(
            instance, pkg_version=pkg_version or "0.1.0", pkg_name=pkg_name
        )

    def render_default_namespace(self) -> dict[str, Any]:
        namespace = cast(
            ExampleInstanceSettings, self.instance_settings
        ).instance_namespace
        obj_dict = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": namespace, "labels": self.default_labels},
            "spec": {},
            "status": {},
        }

        logger.info(f"{obj_dict=}")
        return obj_dict

    def render_default_deployment(self) -> dict[str, Any]:
        instance = cast(ExampleInstanceSettings, self.instance_settings)
        namespace = instance.instance_namespace
        volumes, volume_mounts = [], []
        if instance.volume_mount:
            volume_mounts.append(
                {
                    "name": instance.volume_mount.volume_name,
                    "mountPath": instance.volume_mount.mount_path,
                }
            )
            volumes.append(
                {
                    "name": instance.volume_mount.volume_name,
                    "configMap": {
                        "optional": False,
                        "name": instance.configmap_name,
                    },
                }
            )
        obj_dict = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "labels": self.default_labels,
                "name": f"{instance.deployment_name}",
                "namespace": namespace,
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/instance":
                        f"{instance.instance_name}",  # fmt: skip
                        "app.kubernetes.io/name": f"{self.pkg_name}",
                    }
                },
                "template": {
                    "metadata": {"labels": self.default_labels},
                    "spec": {
                        "containers": [
                            {
                                "image": instance.image_name_with_tag or "busybox:1.32",
                                "imagePullPolicy": "IfNotPresent",
                                "livenessProbe": {
                                    "httpGet": {"path": "/health", "port": "http"},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                    "failureThreshold": 3,
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": "/health", "port": "http"},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                    "failureThreshold": 3,
                                },
                                "name": f"{self.pkg_name}",
                                "args": instance.args,
                                "ports": [
                                    {
                                        "containerPort": 8000,
                                        "name": "http",
                                        "protocol": "TCP",
                                    }
                                ],
                                "resources": {
                                    "limits": {"cpu": "100m", "memory": "128Mi"},
                                    "requests": {"cpu": "50m", "memory": "96Mi"},
                                },
                                "securityContext": {},
                                "volumeMounts": volume_mounts,
                            }
                        ],
                        "securityContext": {},
                        "serviceAccountName": instance.service_account_name,
                        "volumes": volumes,
                    },
                },
            },
        }

        logger.info(f"{obj_dict=}")

        return obj_dict

    def render_default_service(self) -> dict[str, Any]:
        instance = cast(ExampleInstanceSettings, self.instance_settings)
        namespace = instance.instance_namespace
        obj_dict = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "labels": self.default_labels,
                "name": f"{instance.service_name}",
                "namespace": namespace,
            },
            "spec": {
                "ports": [
                    {
                        "name": "http",
                        "port": 8000,
                        "protocol": "TCP",
                        "targetPort": "http",
                    }
                ],
                "selector": {
                    "app.kubernetes.io/instance": f"{instance.instance_name}",
                    "app.kubernetes.io/name": f"{self.pkg_name}",
                },
                "type": "ClusterIP",
            },
        }
        logger.info(f"{obj_dict=}")
        return obj_dict

    def render_default_svc_acct(self) -> dict[str, Any]:
        """

        Args:
            instance_settings:

        Returns:

        """
        instance = cast(ExampleInstanceSettings, self.instance_settings)
        namespace = instance.instance_namespace

        obj_dict = {
            "apiVersion": "v1",
            "automountServiceAccountToken": instance.automount_sa_token,
            "kind": "ServiceAccount",
            "metadata": {
                "labels": self.default_labels,
                "name": instance.service_account_name,
                "namespace": namespace,
            },
        }
        logger.info(f"{obj_dict=}")
        return obj_dict

    def render_default_configmap(self):
        instance = cast(ExampleInstanceSettings, self.instance_settings)
        obj_dict = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": instance.configmap_name,
                "namespace": instance.instance_namespace,
                "labels": self.default_labels,
            },
            "data": {".env": "HTTP_PORT=8000\nHTTP_ADDR=0.0.0.0"},
        }

        return obj_dict

    def render(self) -> ManifestSequence:
        """

        Args:
            settings:
            **kwargs:

        Returns:

        """
        seq: list[dict[str, Any]] = [
            self.render_default_namespace(),
            self.render_default_configmap(),
            self.render_default_svc_acct(),
            self.render_default_deployment(),
            self.render_default_service(),
        ]

        return seq
