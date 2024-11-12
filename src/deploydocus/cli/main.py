from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)


@app.command(name="recon")
def reconcile(
    appname: Annotated[str, typer.Argument(help="Application name")],
    filepath: Annotated[str | None, typer.Option(help="Path to script")] = None,
    module: Annotated[str | None, typer.Option(help="Module name")] = None,
    context: Annotated[
        str | None,
        typer.Option(
            help="Context ",
        ),
    ] = None,
):
    """Does the equivalent of a `kubectl apply -f -` with a rendered manifest

    Args:
        module:
        appname: Name of the application
        filepath:
        context:

    Returns:

    """
    print(f"{appname=} {filepath=} {module=} {context=}")


@app.command(name="reverse", help="Uninstall the application defined by the appname")
def uninstall(
    appname: Annotated[str, typer.Argument(help="Application name")],
):
    pass
