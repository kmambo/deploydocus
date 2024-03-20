import functools
import json
import logging
from typing import Any

from kubernetes import config, utils  # type:ignore
from kubernetes.client import (  # type: ignore
    ApiClient,
    ApiException,
    CoreV1Api,
    V1Deployment,
    V1Namespace,
    V1Service,
    V1ServiceAccount,
)

from deploydocus.settings import DefaultSettings

manager = "deploydocus"

logger = logging.getLogger(__name__)


def _apply(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        self: "DefaultChart" = args[0]
        assert isinstance(self, DefaultSettings), (
            "This decorator can only be "
            "applied to methods of "
            "DefaultChart class or its "
            "derived classes"
        )
        ret = method(*args, **kwargs)
        if not self.settings.dry_run:
            try:
                ret = utils.create_from_dict(
                    self._api_client,
                    ret.to_dict(),
                )
                self._seq.append(ret)
            except Exception:
                logger.error("Unable to create kubernetes object")
                self._unwind()
                raise
        return ret

    return wrapper


class DefaultChart:
    settings: DefaultSettings

    _seq: list[
        Any
    ]  # tracks the sequence in which kubernetes objects are created on the cluster.
    _api_client: ApiClient
    _core_v1: CoreV1Api

    def _unwind(self):
        while self._seq:
            o = self._seq.pop()

    def _create_api_client(self, *, context: str | None = None):
        if not context:
            config.load_kube_config()  # use the default chosen context
        else:
            config.load_kube_config(context=context)
        self._api_client = ApiClient()
        self._core_v1 = CoreV1Api(self._api_client)

    def __init__(self, settings: DefaultSettings, *, context: str | None = None):
        """

        Args:
            settings:
            context:
        """
        self._seq = []
        self.settings = settings
        self._create_api_client(context=context)

    def create_default_namespace(self):
        obj_dict = {
            "api_version": "v1",
            "kind": "Namespace",
            "metadata": {
                "labels": {
                    "kubernetes.io/metadata.name": self.settings.app_namespace,
                    "name": self.settings.app_namespace,
                },
                "managed_fields": [
                    {
                        "api_version": "v1",
                        "fields_type": "FieldsV1",
                        "fields_v1": {
                            "f:metadata": {
                                "f:labels": {
                                    ".": {},
                                    "f:kubernetes.io/metadata.name": {},
                                    "f:name": {},
                                }
                            }
                        },
                        "manager": manager,
                        "operation": "Update",
                    }
                ],
                "name": self.settings.app_namespace,
            },
            "spec": {"finalizers": ["kubernetes"]},
        }

        ret = V1Namespace(**obj_dict)
        if not self.settings.dry_run:
            try:
                ret = self.core_v1.create_namespace(body=ret)
                logger.debug(f"Created NS: {ret}")
            except ApiException as exc:
                if (
                    exc.status == 409
                    and exc.reason == "Conflict"
                    and json.loads(exc.body).get("reason") == "AlreadyExists"
                ):
                    ret = self.core_v1.patch_namespace(
                        body=ret, name=ret.metadata["name"]
                    )

        return ret

    def create_default_deployment(
        self,
        *,
        replicas: int = 1,
    ) -> V1Deployment:
        obj_dict = {
            "api_version": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "labels": self.default_labels,
                "name": f"{self.settings.release_name}-{self.settings.chart_name}",
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "match_labels": self.default_selectors
                },
                "template": {
                    "metadata": {"labels": self.default_labels},
                    "spec": {
                        "containers": [
                            {
                                "image": self.settings.image_name_with_tag,
                                "image_pull_policy": "IfNotPresent",
                                "liveness_probe": {
                                    "http_get": {"path": "/", "port": "http"}
                                },
                                "readiness_probe": {
                                    "http_get": {"path": "/", "port": "http"}
                                },
                                "name": f"{self.settings.chart_name}",
                                "ports": [
                                    {
                                        "container_port": 80,
                                        "name": "http",
                                        "protocol": "TCP",
                                    }
                                ],
                                "resources": {
                                    "limits": {"cpu": "100m", "memory": "128Mi"},
                                    "requests": {"cpu": "100m", "memory": "128Mi"},
                                },
                                "security_context": {},
                                "volume_mounts": [
                                    {
                                        "mount_path": "/etc/foo",
                                        "name": "foo",
                                        "read_only": True,
                                    }
                                ],
                            }
                        ],
                        "security_context": {},
                        "service_account_name": f"{self.settings.release_name}-"
                        f"{self.settings.chart_name}",
                        "volumes": [
                            {
                                "name": "foo",
                                "secret": {
                                    "optional": False,
                                    "secret_name": "mysecret",
                                },
                            }
                        ],
                    },
                },
            },
        }

        return V1Deployment(**obj_dict)

    def create_default_service(
        self,
        port=80,
        port_name="http",
        protocol="TCP",
    ) -> V1Service:
        obj_dict = {
            "api_version": "v1",
            "kind": "Service",
            "metadata": {
                "labels": self.default_labels,
            },
            "spec": {
                "ports": [
                    {
                        "name": port_name,
                        "port": port,
                        "protocol": protocol,
                        "target_port": "http",
                    }
                ],
                "selector": {
                    "app.kubernetes.io/instance": f"{self.settings.release_name}",
                    "app.kubernetes.io/name": f"{self.settings.chart_name}",
                },
                "type": "ClusterIP",
            },
        }
        return V1Service(**obj_dict)

    def create_default_sa(self, sa_name: str | None = None) -> V1ServiceAccount:
        """

        Args:
            sa_name: Service account name

        Returns:

        """
        obj_dict = {
            "api_version": "v1",
            "automount_service_account_token": True,
            "kind": "ServiceAccount",
            "metadata": {
                "labels": self.default_labels,
                "name": sa_name
                or f"{self.settings.release_name}-" f"{self.settings.chart_name}",
            },
        }
        return V1ServiceAccount(**obj_dict)

    def install(self, save_state=False, atomic=False, cont=False):
        if not self.settings.dry_run:
            ns = self.create_default_namespace()

            namespace = ns.metadata["name"]
            self.create_default_namespace()

    @property
    def default_labels(self):
        return {
            "app.kubernetes.io/name": self.default_chart_name,
            "app.kubernetes.io/instance": self.default_release_name,
            "app.kubernetes.io/version": self.default_app_version,
            "app.kubernetes.io/managed-by": "deploydocus.io",
            manager: self.default_chart_fullname
        }

    @property
    def default_chart_version(self) -> str:
        return self.settings.chart_version

    @property
    def default_chart_name(self) -> str:
        return self.settings.chart_name

    @property
    def default_chart_fullname(self) -> str:
        return f"{self.default_chart_name}-{self.default_chart_version}"

    @property
    def default_app_version(self) -> str:
        return self.settings.app_version

    @property
    def default_release_name(self) -> str:
        return self.settings.release_name

    @property
    def default_selectors(self) -> dict[str, str]:
        return {
            "app.kubernetes.io/name": self.default_chart_name,
            "app.kubernetes.io/instance": self.default_release_name,
        }

    @property
    def core_v1(self):
        return self._core_v1
