from functools import partial

from kubernetes.client import models  # type: ignore[import-untyped]

Namespace = partial(
    models.V1Namespace, keywords={"api_version": "v1", "kind": "Namespace"}
)
NetworkPolicy = partial(
    models.V1NetworkPolicy,
    keywords={"api_version": "networking.k8s.io/v1", "kind": "NetworkPolicy"},
)
ResourceQuota = partial(
    models.V1ResourceQuota, keywords={"api_version": "v1", "kind": "ResourceQuota"}
)
LimitRange = partial(
    models.V1LimitRange, keywords={"api_version": "v1", "kind": "LimitRange"}
)
PodDisruptionBudget = partial(
    models.V1PodDisruptionBudget,
    keywords={"api_version": "policy/v1", "kind": "PodDisruptionBudget"},
)
ServiceAccount = partial(
    models.V1ServiceAccount, keywords={"api_version": "v1", "kind": "ServiceAccount"}
)
Secret = partial(models.V1Secret, keywords={"api_version": "v1", "kind": "Secret"})
SecretList = partial(
    models.V1SecretList, keywords={"api_version": "v1", "kind": "SecretList"}
)
ConfigMap = partial(
    models.V1ConfigMap, keywords={"api_version": "v1", "kind": "ConfigMap"}
)
StorageClass = partial(
    models.V1StorageClass,
    keywords={"api_version": "storage.k8s.io/v1", "kind": "StorageClass"},
)
PersistentVolume = partial(
    models.V1PersistentVolume,
    keywords={"api_version": "v1", "kind": "PersistentVolume"},
)
PersistentVolumeClaim = partial(
    models.V1PersistentVolumeClaim,
    keywords={"api_version": "v1", "kind": "PersistentVolumeClaim"},
)
CustomResourceDefinition = partial(
    models.V1CustomResourceDefinition,
    keywords={
        "api_version": "apiextensions.k8s.io/v1",
        "kind": "CustomResourceDefinition",
    },
)
ClusterRole = partial(
    models.V1ClusterRole,
    keywords={"api_version": "rbac.authorization.k8s.io/v1", "kind": "ClusterRole"},
)
ClusterRoleList = partial(
    models.V1ClusterRoleList,
    keywords={"api_version": "rbac.authorization.k8s.io/v1", "kind": "ClusterRoleList"},
)
ClusterRoleBinding = partial(
    models.V1ClusterRoleBinding,
    keywords={
        "api_version": "rbac.authorization.k8s.io/v1",
        "kind": "ClusterRoleBinding",
    },
)
ClusterRoleBindingList = partial(
    models.V1ClusterRoleBindingList,
    keywords={
        "api_version": "rbac.authorization.k8s.io/v1",
        "kind": "ClusterRoleBindingList",
    },
)
Role = partial(
    models.V1Role,
    keywords={"api_version": "rbac.authorization.k8s.io/v1", "kind": "Role"},
)
RoleList = partial(
    models.V1RoleList,
    keywords={"api_version": "rbac.authorization.k8s.io/v1", "kind": "RoleList"},
)
RoleBinding = partial(
    models.V1RoleBinding,
    keywords={"api_version": "rbac.authorization.k8s.io/v1", "kind": "RoleBinding"},
)
RoleBindingList = partial(
    models.V1RoleBindingList,
    keywords={"api_version": "rbac.authorization.k8s.io/v1", "kind": "RoleBindingList"},
)
Service = partial(models.V1Service, keywords={"api_version": "v1", "kind": "Service"})
DaemonSet = partial(
    models.V1DaemonSet, keywords={"api_version": "apps/v1", "kind": "DaemonSet"}
)
Pod = partial(models.V1Pod, keywords={"api_version": "v1", "kind": "Pod"})
ReplicationController = partial(
    models.V1ReplicationController,
    keywords={"api_version": "v1", "kind": "ReplicationController"},
)
ReplicaSet = partial(
    models.V1ReplicaSet, keywords={"api_version": "apps/v1", "kind": "ReplicaSet"}
)
Deployment = partial(
    models.V1Deployment, keywords={"api_version": "apps/v1", "kind": "Deployment"}
)
HorizontalPodAutoscaler = partial(
    models.V2HorizontalPodAutoscaler,
    keywords={"api_version": "autoscaling/v2", "kind": "HorizontalPodAutoscaler"},
)
StatefulSet = partial(
    models.V1StatefulSet, keywords={"api_version": "apps/v1", "kind": "StatefulSet"}
)
Job = partial(models.V1Job, keywords={"api_version": "batch/v1", "kind": "Job"})
CronJob = partial(
    models.V1CronJob, keywords={"api_version": "batch/v1", "kind": "CronJob"}
)
Ingress = partial(
    models.V1Ingress,
    keywords={"api_version": "networking.k8s.io/v1", "kind": "Ingress"},
)
APIService = partial(
    models.V1APIService,
    keywords={"api_version": "apiregistration.k8s.io/v1", "kind": "APIService"},
)
