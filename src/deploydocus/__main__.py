import typer

app = typer.Typer()


@app.command()
def template(): ...


# @app.command()
# def gen_app(
#     pkg_name: str,
#     json_file: Annotated[Path, typer.Option(help="Path to a .env file")] = None,
#     context: Annotated[str | None,
#     typer.Option(help="kubernetes context name")] = None,
# ):
# print(f"{json_file=}")
# default_setting = PkgSettings()
# chart = DefaultChart(pkg_name, settings_file=json_file)
# ns = chart.create_default_namespace()
# deployment = chart.create_default_deployment()
# service = chart.create_default_service()


if __name__ == "__main__":
    app()
