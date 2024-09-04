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


def test_helmrepo_pull_https(helm_repo_chart_url_https):
    hc = HelmChart(helm_repo_chart_url_https)
    chart_name = cast(HelmRepoChart, hc.chart).chart_name
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        hc.pull(tmpdir)
        assert (Path(tmpdir) / chart_name).is_dir(), f"{tree(tmpdir)}"
        assert (Path(tmpdir) / f"{chart_name}/templates").is_dir(), f"{tree(tmpdir)}"


def test_helmrepo_pull_oci(helm_repo_chart_url_oci):
    hc = HelmChart(helm_repo_chart_url_oci)
    chart_name = cast(HelmRepoChart, hc.chart).chart_name
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        hc.pull(tmpdir)
        assert (Path(tmpdir) / chart_name).is_dir(), f"{tree(tmpdir)}"
        assert (Path(tmpdir) / f"{chart_name}/templates").is_dir(), f"{tree(tmpdir)}"
