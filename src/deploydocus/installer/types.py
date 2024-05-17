from typing import Any, Protocol, Sequence, TypeAlias


class K8sModels(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    def to_str(self) -> str: ...


ManifestDict: TypeAlias = dict[str, Any] | K8sModels
ManifestSequence: TypeAlias = Sequence[ManifestDict]
ManifestAll: TypeAlias = ManifestDict | ManifestSequence


def is_k8s_model(model: Any) -> bool:
    """Returns true if an object is a Python class representing
    a Kubernetes object

    Args:
        model:

    Returns:

    """
    return (
        hasattr(model, "to_dict")
        and hasattr(model, "to_str")
        and callable(model.to_dict)
        and callable(model.to_str)
    )
