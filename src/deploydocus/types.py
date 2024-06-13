from collections import OrderedDict
from typing import Any, NotRequired, Sequence, TypeAlias, TypedDict, Union

from kubernetes.client import models as _k8s_models

SUPPORTED_KINDS: OrderedDict[str, str] = OrderedDict(
    [
        ("Namespace", "v1"),
        ("NetworkPolicy", "networking.k8s.io/v1"),
        ("ResourceQuota", "v1"),
        ("LimitRange", "v1"),
        ("PodDisruptionBudget", "policy/v1"),
        ("ServiceAccount", "v1"),
        ("Secret", "v1"),
        ("SecretList", "v1"),
        ("ConfigMap", "v1"),
        ("StorageClass", "storage.k8s.io/v1"),
        ("PersistentVolume", "v1"),
        ("PersistentVolumeClaim", "v1"),
        ("CustomResourceDefinition", "apiextensions.k8s.io/v1"),
        ("ClusterRole", "rbac.authorization.k8s.io/v1"),
        ("ClusterRoleList", "rbac.authorization.k8s.io/v1"),
        ("ClusterRoleBinding", "rbac.authorization.k8s.io/v1"),
        ("ClusterRoleBindingList", "rbac.authorization.k8s.io/v1"),
        ("Role", "rbac.authorization.k8s.io/v1"),
        ("RoleList", "rbac.authorization.k8s.io/v1"),
        ("RoleBinding", "rbac.authorization.k8s.io/v1"),
        ("RoleBindingList", "rbac.authorization.k8s.io/v1"),
        ("Service", "v1"),
        ("DaemonSet", "apps/v1"),
        ("Pod", "v1"),
        ("ReplicationController", "v1"),
        ("ReplicaSet", "apps/v1"),
        ("Deployment", "apps/v1"),
        ("HorizontalPodAutoscaler", "autoscaling/v2"),
        ("StatefulSet", "apps/v1"),
        ("Job", "batch/v1"),
        ("CronJob", "batch/v1"),
        ("Ingress", "networking.k8s.io/v1"),
        ("APIService", "apiregistration.k8s.io/v1"),
    ]
)

LabelsSelector = TypedDict(
    "LabelsSelector",
    {
        "app.kubernetes.io/instance": str,
        "app.kubernetes.io/managed-by": str,
        "app.kubernetes.io/name": NotRequired[str],
    },
)

LabelsDict = TypedDict(
    "LabelsDict",
    {
        "app.kubernetes.io/instance": str,
        "app.kubernetes.io/name": str,
        "app.kubernetes.io/version": str,
        "deploydocus-pkg": str,
        "app.kubernetes.io/managed-by": str,
    },
)


def import_k8s_model(kind: str) -> type:
    api_version = SUPPORTED_KINDS[kind]
    group, _, version = api_version.partition("/")
    if version == "":
        version = group
    return getattr(_k8s_models, f"{version.capitalize()}{kind}")


# class K8sModel(Protocol):
#     def to_dict(self) -> dict[str, Any]: ...
#
#     def to_str(self) -> str: ...
#
#
# class K8sListModel(Protocol):
#     def to_dict(self) -> dict[str, Any]: ...
#
#     def to_str(self) -> str: ...
#
#     @property
#     def items(self) -> list[K8sModel]: ...

all_nonlist_models = [
    import_k8s_model(k) for k in SUPPORTED_KINDS.keys() if k[-4:] != "List"
]
all_list_models = [
    import_k8s_model(k) for k in SUPPORTED_KINDS.keys() if k[-4:] == "List"
]
K8sModel = Union[*all_nonlist_models]  # type: ignore[valid-type]
K8sListModel: TypeAlias = Union[*all_list_models]  # type: ignore[valid-type]
K8sModelSequence: TypeAlias = Sequence[K8sModel]
ManifestDict: TypeAlias = dict[str, Any] | K8sModel | K8sListModel
ManifestSequence: TypeAlias = Sequence[ManifestDict]
ManifestAll: TypeAlias = ManifestDict | ManifestSequence
