from collections import OrderedDict
from typing import Any, LiteralString, Mapping, NotRequired, Sequence, TypedDict, Union

from kubernetes.client.models import (  # type: ignore[import-untyped]
    V1APIService,
    V1ClusterRole,
    V1ClusterRoleBinding,
    V1ClusterRoleBindingList,
    V1ClusterRoleList,
    V1ConfigMap,
    V1CronJob,
    V1CustomResourceDefinition,
    V1DaemonSet,
    V1Deployment,
    V1HorizontalPodAutoscaler,
    V1Ingress,
    V1Job,
    V1LimitRange,
    V1Namespace,
    V1NetworkPolicy,
    V1PersistentVolume,
    V1PersistentVolumeClaim,
    V1Pod,
    V1PodDisruptionBudget,
    V1ReplicaSet,
    V1ReplicationController,
    V1ResourceQuota,
    V1Role,
    V1RoleBinding,
    V1RoleBindingList,
    V1RoleList,
    V1Secret,
    V1SecretList,
    V1Service,
    V1ServiceAccount,
    V1StatefulSet,
    V1StorageClass,
)

SUPPORTED_KINDS: OrderedDict[LiteralString, LiteralString] = OrderedDict(
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

SUPPORTED_KUBERNETES_KINDS: list[str] = list(SUPPORTED_KINDS.keys())

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

type K8sModel = Union[
    V1APIService,
    V1ClusterRoleBinding,
    V1ClusterRole,
    V1ConfigMap,
    V1CronJob,
    V1CustomResourceDefinition,
    V1DaemonSet,
    V1Deployment,
    V1HorizontalPodAutoscaler,
    V1Ingress,
    V1Job,
    V1LimitRange,
    V1Namespace,
    V1NetworkPolicy,
    V1PersistentVolume,
    V1PersistentVolumeClaim,
    V1Pod,
    V1PodDisruptionBudget,
    V1ReplicaSet,
    V1ReplicationController,
    V1ResourceQuota,
    V1RoleBinding,
    V1Role,
    V1Secret,
    V1Service,
    V1ServiceAccount,
    V1StatefulSet,
    V1StorageClass,
]
K8sListModel = Union[
    V1ClusterRoleBindingList,
    V1ClusterRoleList,
    V1RoleBindingList,
    V1RoleList,
    V1SecretList,
]
K8sModelSequence = list[K8sModel]
# TODO: Deprecate the ones below
ManifestDict = Mapping[str, Any] | K8sModel | K8sListModel
ManifestSequence = Sequence[ManifestDict]
ManifestAll = ManifestDict | ManifestSequence
