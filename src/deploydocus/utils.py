import logging
from typing import Any


class UnsupportedObjectType(Exception): ...


logger = logging.getLogger(__name__)


# def is_empty(obj: Any) -> bool:
#     _type = type(obj)
#     if issubclass(_type, )


def remove_empty_val(obj_dict: Any) -> dict[str, Any] | list[Any]:
    """Removes from the dictionary, any key-value pair whose value is an empty

    Args:
        obj_dict:

    Returns:

    """
    try:
        if isinstance(obj_dict, dict):
            return {
                k: v
                for k, v in obj_dict.items()
                if isinstance(v, (int, float, complex))
                or (isinstance(v, str) and bool(v))
                or (bool(v) and remove_empty_val(v))
            }
        if isinstance(obj_dict, list):
            return [
                v
                for v in obj_dict
                if isinstance(v, (int, float, complex))
                or (isinstance(v, str) and bool(v))
                or (bool(v) and remove_empty_val(v))
            ]
        logger.error(f"{obj_dict=}")
        raise Exception(f"{obj_dict=}")
    except AttributeError:
        logger.error(f"{obj_dict=}")
        raise
    except UnsupportedObjectType as e:
        raise Exception(f"{obj_dict}") from e


def delete_from_dict(
    k8s_client, data, verbose=False, namespace="default", **kwargs
) -> bool:
    """

    Args:
        k8s_client:
        data:
        verbose:
        namespace:
        **kwargs:

    Returns:

    """
    ...
