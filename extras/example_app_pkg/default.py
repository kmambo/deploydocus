import logging
from typing import Any, Sequence, override

from deploydocus.installer.pkg import AbstractK8sPkg
from deploydocus.installer.settings import InstanceSettings
from deploydocus.logging.configure import configure_logging

from .settings import ExampleInstanceSettings, ExamplePkgSettings

configure_logging()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExamplePkg(AbstractK8sPkg):
    def __init__(self, pkg_name: str | None = None):
        super().__init__(pkg_name, pkg_settings_class=ExamplePkgSettings)

    def render_default_namespace(
        self, instance_settings: ExampleInstanceSettings
    ) -> dict[str, Any] | None:
        namespace = (
            instance_settings.instance_namespace or self.pkg_settings.pkg_namespace
        )
        obj_dict = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": namespace},
            "spec": {},
            "status": {},
        }
        logger.info(f"{obj_dict=}")
        return obj_dict

    def render_default_deployment(
        self, instance_settings: ExampleInstanceSettings
    ) -> dict[str, Any]:
        namespace = (
            instance_settings.instance_namespace or self.pkg_settings.pkg_namespace
        )
        volumes, volume_mounts = [], []
        if instance_settings.volume_mount:
            volume_mounts.append(
                {
                    "name": instance_settings.volume_mount.volume_name,
                    "mountPath": instance_settings.volume_mount.mount_path,
                }
            )
            volumes.append(
                {
                    "name": instance_settings.volume_mount.volume_name,
                    "configMap": {
                        "optional": False,
                        "name": instance_settings.configmap_name,
                    },
                }
            )
        obj_dict = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "labels": self.default_labels(instance_settings),
                "name": f"{instance_settings.deployment_name}",
                "namespace": namespace,
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/instance":
                        f"{instance_settings.instance_name}",  # fmt: skip
                        "app.kubernetes.io/name": f"{self.pkg_settings.pkg_name}",
                    }
                },
                "template": {
                    "metadata": {"labels": self.default_labels(instance_settings)},
                    "spec": {
                        "containers": [
                            {
                                "image": instance_settings.image_name_with_tag
                                or "busybox:1.32",
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
                                "name": f"{self.pkg_settings.pkg_name}",
                                "args": instance_settings.args,
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
                        "serviceAccountName": instance_settings.service_account_name,
                        "volumes": volumes,
                    },
                },
            },
        }

        logger.info(f"{obj_dict=}")

        return obj_dict

    def render_default_service(
        self, instance_settings: ExampleInstanceSettings
    ) -> dict[str, Any]:
        namespace = (
            instance_settings.instance_namespace or self.pkg_settings.pkg_namespace
        )
        obj_dict = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "labels": self.default_labels(instance_settings),
                "name": f"{instance_settings.service_name}",
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
                    "app.kubernetes.io/instance": f"{instance_settings.instance_name}",
                    "app.kubernetes.io/name": f"{self.pkg_settings.pkg_name}",
                },
                "type": "ClusterIP",
            },
        }
        logger.info(f"{obj_dict=}")
        return obj_dict

    def render_default_svc_acct(
        self, instance_settings: ExampleInstanceSettings
    ) -> dict[str, Any]:
        """

        Args:
            instance_settings:

        Returns:

        """
        namespace = (
            instance_settings.instance_namespace or self.pkg_settings.pkg_namespace
        )
        obj_dict = {
            "apiVersion": "v1",
            "automountServiceAccountToken": instance_settings.automount_sa_token,
            "kind": "ServiceAccount",
            "metadata": {
                "labels": self.default_labels(instance_settings),
                "name": instance_settings.service_account_name,
                "namespace": namespace,
            },
        }
        logger.info(f"{obj_dict=}")
        return obj_dict

    def default_labels(self, instance_settings: InstanceSettings, **kwargs):
        pkg_name, pkg_version, instance_name, instance_version = (
            kwargs.get("pkg_name") or self.pkg_settings.pkg_name,
            kwargs.get("pkg_version") or self.pkg_settings.pkg_version,
            kwargs.get("instance_name") or instance_settings.instance_name,
            kwargs.get("instance_version") or instance_settings.instance_version,
        )
        _def_label = {
            "app.kubernetes.io/name": pkg_name,
            "app.kubernetes.io/instance": instance_name,
            "app.kubernetes.io/version": instance_version,
            "app.kubernetes.io/managed-by": self.deploydocus_domain,
            "deploydocus-pkg": f"{pkg_name}-{pkg_version}",
        }
        return _def_label

    def render_default_configmap(self, instance_settings: ExampleInstanceSettings):
        obj_dict = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": instance_settings.configmap_name,
                "namespace": instance_settings.instance_namespace,
                "labels": self.default_labels(instance_settings),
            },
            "data": {".env": "HTTP_PORT=8000\nHTTP_ADDR=0.0.0.0"},
        }

        return obj_dict

    @override
    def render(self, settings: ExampleInstanceSettings, **kwargs) -> Sequence[dict]:
        """

        Args:
            settings:
            **kwargs:

        Returns:

        """
        settings_new = settings.model_copy(update=kwargs, deep=True)
        seq: list[dict[str, Any]] = [
            self.render_default_namespace(settings_new),
            self.render_default_configmap(settings_new),
            self.render_default_svc_acct(settings_new),
            self.render_default_deployment(settings_new),
            self.render_default_service(settings_new),
        ]

        return seq
