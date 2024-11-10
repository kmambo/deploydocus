from typing import Annotated, Optional

import typer

app = typer.Typer(no_args_is_help=True)


@app.command(name="recon")
def reconcile(
    appname: str,  # Annotated[str, typer.Argument(help="Application name")],
    filepath: Optional[
        str
    ] = None,  # Annotated[str | None, typer.Option(default=None, help="Path to script")],
    module: Optional[
        str
    ] = None,  # Annotated[str | None, typer.Option(default=None, help="Module name")],
    context: Optional[
        str
    ] = None,  # Annotated[str | None, typer.Option(help="Context ", default=None)],
):
    """Reconcile

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
