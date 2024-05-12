from typing import Any, Protocol, Sequence, TypeAlias


class K8sModels(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    def to_str(self) -> str: ...


ManifestDict: TypeAlias = dict[str, Any] | K8sModels
ManifestAll: TypeAlias = ManifestDict | Sequence[ManifestDict]
