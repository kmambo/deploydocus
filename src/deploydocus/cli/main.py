import logging
from typing import Annotated, Literal

import typer

from deploydocus.backends import StateDb

from .. import Kustomization
from ..package import AbstractK8sPkg

app = typer.Typer(no_args_is_help=True)

logger = logging.getLogger(__name__)


def _xnor_and_resolve(module, fetchable_url) -> AbstractK8sPkg | Kustomization:
    """Check that only one of module

    Args:
        module:
        fetchable_url:

    Returns:

    """
    assert (
        module and not fetchable_url or fetchable_url and not module
    ), "Only one of module and filepath must be provided"
    # TODO


def _apply_new(appname, filepath):
    pass


def _apply_patch(appname, filepath):
    pass


@app.command(name="recon")
def reconcile(
    appname: Annotated[str, typer.Argument(help="Application name")],
    backend: StateDb,
    fetchable_url: Annotated[str | None, typer.Option(help="Path to ")] = None,
    module: Annotated[str | None, typer.Option(help="Module name")] = None,
    context: Annotated[
        str | None,
        typer.Option(
            help="Context ",
        ),
    ] = None,
    op: Literal["insert", "create", "delete", "replace", "edit"] = "insert",
):
    """Does the equivalent of a `kubectl apply -f -` with a rendered manifest.
    The `appname` is what needs to be "unique" for that cluster in the backend.
    If there is already an appname, then the assumption is to either delete or patch.

    Args:
        backend:
        module: Name of application module from the Python class in package
        appname: Name of the application.
        fetchable_url: Useful in testing where the module being
        context: The cluster context to use. what you are able to reconcile to the
        cluster depends on the user (and permissions) associated will be dictated
        by the permissions from
        op:

    Returns:

    """
    logger.debug("{appname=} {fetchable_url=} {module=} {context=}")
    resolved_src = _xnor_and_resolve(module, fetchable_url)  # noqa: F841
    match op:
        case "insert" | "create":
            _apply_new(appname=appname, filepath=fetchable_url or module)
        case "edit" | "patch":
            _apply_patch(appname=appname, filepath=fetchable_url or module)
        case "rename":
            # TODO
            ...
        case "delete" | "erase":
            # TODO
            ...
        case _:
            raise ValueError(f"Don't know {op=}")


@app.command(name="reverse", help="Uninstall the application defined by the appname")
def uninstall(
    appname: Annotated[str, typer.Argument(help="Application name")],
):
    """

    Args:
        appname:

    Returns:

    """
    pass
