from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from plumbum import local

from deploydocus.appstate.helm3 import HelmChart, HelmRepoChart
from deploydocus.appstate.sources import GitRepo

ls = local["ls"]


def test_helm_from_gitrepo():
    gr_url = "https://github.com/helm/examples"
    gr = GitRepo(url=gr_url)
    helloworld = "charts/hello-world"
    hc = HelmChart(gr, helloworld)
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        hc.pull(tmpdir, root=helloworld)
        chart_root = Path(helloworld).parts[-1]
        assert (Path(tmpdir) / chart_root).is_dir(), f"{tree(tmpdir)}"


def test_helmrepo_pull():
    helm_chart_url = "https://owkin.github.io/charts/pypiserver"

    hc = HelmChart(helm_chart_url)
    chart_name = cast(HelmRepoChart, hc.chart).chart_name
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        hc.pull(tmpdir)
        assert (Path(tmpdir) / chart_name).is_dir(), f"{tree(tmpdir)}"
        assert (Path(tmpdir) / f"{chart_name}/templates").is_dir(), f"{tree(tmpdir)}"
