from pathlib import Path
from typing import Annotated

import kubernetes
import typer

from deploydocus.chart.default import DefaultChart
from deploydocus.settings import DefaultSettings

app = typer.Typer()


def _to_yaml(obj):
    ret = obj.to_dict()


@app.command()
def template(): ...


@app.command()
def gen_app(
    env_file: Annotated[Path, typer.Option(help="Path to a .env file")] = Path(".env"),
    apply: Annotated[bool, typer.Option(help="--apply")] = False,
):
    print(f"{env_file=}")
    default_setting = DefaultSettings(_env_file=env_file)
    chart = DefaultChart(settings=default_setting)
    deployment = chart.create_default_deployment()
    print(deployment.to_dict())
    service = chart.create_default_service()
    print(service.to_dict())
    if apply:
        kubernetes.config.load_kube_config()
        k8s_apps_v1 = kubernetes.client.AppsV1Api()
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=deployment.to_dict(), namespace="default"
        )


if __name__ == "__main__":
    app()
