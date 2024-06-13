from typing import Any, NotRequired, Protocol, Sequence, TypeAlias, TypedDict

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


class K8sModel(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    def to_str(self) -> str: ...


class K8sListModel(Protocol):
    def to_dict(self) -> dict[str, Any]: ...
    def to_str(self) -> str: ...
    @property
    def items(self) -> list[K8sModel]: ...


ManifestDict: TypeAlias = dict[str, Any] | K8sModel | K8sListModel
ManifestSequence: TypeAlias = Sequence[ManifestDict]
ManifestAll: TypeAlias = ManifestDict | ManifestSequence
