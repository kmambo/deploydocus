from pathlib import Path
from typing import Annotated

import typer

from deploydocus.chart.default import DefaultChart
from deploydocus.settings import DefaultSettings

app = typer.Typer()


@app.command()
def template(): ...


@app.command()
def gen_app(
    env_file: Annotated[Path, typer.Option(help="Path to a .env file")] = Path(".env"),
    context: Annotated[str | None, typer.Option(help="kubernetes context name")] = None,
):
    print(f"{env_file=}")
    default_setting = DefaultSettings(_env_file=env_file)
    chart = DefaultChart(settings=default_setting, context=context)
    ns = chart.create_default_namespace()
    deployment = chart.create_default_deployment()
    # print(deployment.to_dict())
    service = chart.create_default_service()
    # print(service.to_dict())


if __name__ == "__main__":
    app()
