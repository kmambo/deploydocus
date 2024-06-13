import logging
from typing import Any, Callable, LiteralString, cast

from kubernetes import client
from kubernetes.client import ApiClient
from kubernetes.client.rest import ApiException
from kubernetes.utils import FailToCreateError
from kubernetes.utils.create_from_yaml import (  # type: ignore
    LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE,
    UPPER_FOLLOWED_BY_LOWER_RE,
)

from deploydocus import SUPPORTED_KINDS
from deploydocus.types import K8sListModel, K8sModel


class FailToDeleteError(FailToCreateError): ...


class UnsupportedObjectType(Exception): ...


_valid_ops: list[LiteralString] = [
    "create",
    "delete",
    "delete_collection",
    "get",
    "list",
    "patch",
    "update",
]  # TODO: add support for 'watch'


class UnsupportedOperation(Exception): ...


logger = logging.getLogger(__name__)


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


def k8s_api_class(kind: str) -> type:
    api_version = SUPPORTED_KINDS[kind]
    group, _, version = api_version.partition("/")
    if version == "":
        version = group
        group = "core"
    group = "".join(group.rsplit(".k8s.io", 1))
    group = "".join(word.capitalize() for word in group.split("."))
    ret = "{0}{1}Api".format(group, version.capitalize())
    return getattr(client, ret)


def k8s_crud_callable(
    *,
    kind: str,
    k8s_client: ApiClient,
    op: str,
) -> tuple[Callable[..., K8sModel | K8sListModel], bool]:
    """Create a callable that supports the given operation

    Args:
        op:
        k8s_client:
        kind:

    Returns: A tuple with the first element being a callable that supports the
    requested operation and the second is a boolean which indicates if this is
    a namespaced op or not

    """
    # TODO: replace labels_selector type to LabelsSelectorDict type
    assert op in _valid_ops
    api_class: type = k8s_api_class(kind)
    api_class_obj = api_class(k8s_client)
    if kind.endswith("List"):
        kind = kind[:-4]
    method_suffix = UPPER_FOLLOWED_BY_LOWER_RE.sub(r"\1_\2", kind)
    method_suffix = LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE.sub(
        r"\1_\2", method_suffix
    ).lower()
    fn_namespaced, fn_nonnamespaced = (
        f"{op}_namespaced_{method_suffix}",
        f"{op}_{method_suffix}",
    )

    if hasattr(api_class_obj, fn_namespaced):
        # Namespaced object
        return getattr(api_class_obj, fn_namespaced), True
    elif hasattr(api_class_obj, fn_nonnamespaced):
        # Non-namespaced object
        return getattr(api_class_obj, fn_nonnamespaced), False
    else:
        raise UnsupportedOperation(
            f"The object of kind {kind} does not support a/an "
            f"{op} operation. "
            f"{fn_namespaced}/{fn_nonnamespaced}"
        )


def delete_from_dict(
    k8s_client: ApiClient, data, verbose=False, namespace="default", **kwargs
):
    """Delete a single

    Args:
        k8s_client: an ApiClient object, initialized with the client args.
        data: A dictionary holding valid kubernetes objects
        verbose: If True, print confirmation from the delete action.
                Default is False.
        namespace: Contains the namespace to delete all
                resources inside. The namespace must preexist otherwise
                the resource creation will fail. If the API object in
                the yaml file already contains a namespace definition
                this parameter has no effect.
        **kwargs:

    Returns:
        The deleted kubernetes API objects.

    Raises:
        FailToDeleteError which holds list of `client.rest.ApiException`
        instances for each object that failed to delete.
    """
    # If it is a list type, will need to iterate its items
    api_exceptions = []
    k8s_objects = []

    if isinstance(data, dict):
        data = cast(K8sModel, data).to_dict()
    if "List" in data["kind"]:
        kind = data["kind"].replace("List", "")
        for yml_object in reversed(data["items"]):
            if kind != "":
                yml_object["apiVersion"] = data["apiVersion"]
                yml_object["kind"] = kind
            try:
                deleted = delete_from_yaml_single_item(
                    k8s_client, yml_object, verbose, namespace=namespace, **kwargs
                )
                if deleted:
                    k8s_objects.append(deleted)
            except client.rest.ApiException as api_exception:
                api_exceptions.append(api_exception)
    else:
        # This is a single object. Call the single item method
        try:
            deleted = delete_from_yaml_single_item(
                k8s_client, data, verbose, namespace=namespace, **kwargs
            )
            if deleted:
                k8s_objects.append(deleted)
        except ApiException as api_exception:
            api_exceptions.append(api_exception)

    # In case we have exceptions waiting for us, raise them
    if api_exceptions:
        raise FailToDeleteError(api_exceptions)

    return k8s_objects


def delete_from_model(
    k8s_client: ApiClient, data, verbose=False, namespace="default", **kwargs
):
    api_exceptions = []
    k8s_objects = []

    if "List" in data.kind:
        kind = data.kind.replace("List", "")
        for yml_object in reversed(data.items):
            if kind != "":
                yml_object.api_version = data.api_version
                yml_object.kind = kind
            try:
                deleted = delete_single_model(
                    k8s_client, yml_object, verbose, namespace=namespace, **kwargs
                )
                if deleted:
                    k8s_objects.append(deleted)
            except client.rest.ApiException as api_exception:
                api_exceptions.append(api_exception)
    else:
        # This is a single object. Call the single item method
        try:
            deleted = delete_single_model(
                k8s_client, data, verbose, namespace=namespace, **kwargs
            )
            if deleted:
                k8s_objects.append(deleted)
        except ApiException as api_exception:
            api_exceptions.append(api_exception)

    if api_exceptions:
        raise FailToDeleteError(api_exceptions)

    return k8s_objects


def delete_from_yaml_single_item(k8s_client, yml_object, verbose=False, **kwargs):
    """

    Args:
        k8s_client:
        yml_object:
        verbose:
        **kwargs:

    Returns:

    Raises:
        ApiException: If there is an APiException it propagates except if
        the .status attribute of the exception is 404
    """
    group, _, version = yml_object["apiVersion"].partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    # Only replace the last instance
    group = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group = "".join(word.capitalize() for word in group.split("."))
    fcn_to_call = "{0}{1}Api".format(group, version.capitalize())
    k8s_api = getattr(client, fcn_to_call)(k8s_client)
    # Replace CamelCased action_type into snake_case
    kind = yml_object["kind"]
    kind = UPPER_FOLLOWED_BY_LOWER_RE.sub(r"\1_\2", kind)
    kind = LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE.sub(r"\1_\2", kind).lower()
    # Expect the user to delete namespaced objects more often
    try:
        if hasattr(k8s_api, "delete_namespaced_{0}".format(kind)):
            # Decide which namespace we are going to put the object in,
            # if any
            name = yml_object["metadata"]["name"]
            if "namespace" in yml_object["metadata"]:
                namespace = yml_object["metadata"]["namespace"]
                kwargs["namespace"] = namespace

            resp = getattr(k8s_api, "delete_namespaced_{0}".format(kind))(
                name=name, **kwargs
            )
        else:
            kwargs.pop("namespace")
            name = yml_object["metadata"]["name"]
            resp = getattr(k8s_api, "delete_{0}".format(kind))(name=name, **kwargs)
    except ApiException as ae:
        if ae.status == 404:
            return None
        raise
    if verbose:
        msg = "{0} deleted.".format(kind)
        if hasattr(resp, "status"):
            msg += " status='{0}'".format(str(resp.status))
        logger.info(msg)
    return resp


def delete_single_model(k8s_client, yml_object, verbose=False, **kwargs):
    group, _, version = yml_object.api_version.partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    # Only replace the last instance
    group = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group = "".join(word.capitalize() for word in group.split("."))
    fcn_to_call = "{0}{1}Api".format(group, version.capitalize())
    k8s_api = getattr(client, fcn_to_call)(k8s_client)
    # Replace CamelCased action_type into snake_case
    kind = yml_object.kind
    kind = UPPER_FOLLOWED_BY_LOWER_RE.sub(r"\1_\2", kind)
    kind = LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE.sub(r"\1_\2", kind).lower()
    # Expect the user to delete namespaced objects more often
    try:
        if hasattr(k8s_api, "delete_namespaced_{0}".format(kind)):
            # Decide which namespace we are going to put the object in,
            # if any
            name = yml_object.metadata.name
            if hasattr(yml_object.metadata, "namespace"):
                namespace = yml_object.metadata.namespace
                kwargs["namespace"] = namespace

            resp = getattr(k8s_api, "delete_namespaced_{0}".format(kind))(
                name=name, **kwargs
            )
        else:
            kwargs.pop("namespace")
            name = yml_object.metadata.name
            resp = getattr(k8s_api, "delete_{0}".format(kind))(name=name, **kwargs)
    except ApiException as ae:
        if ae.status == 404:
            return None
        raise
    if verbose:
        msg = "{0} deleted.".format(kind)
        if hasattr(resp, "status"):
            msg += " status='{0}'".format(str(resp.status))
        logger.info(msg)
    return resp


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
