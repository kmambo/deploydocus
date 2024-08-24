from pathlib import Path
from tempfile import TemporaryDirectory

from plumbum import local

from deploydocus.installer.helm3 import HelmChart
from deploydocus.installer.sources import GitRepo

ls = local["ls"]


def test_helm_pull_git():
    gr_url = "https://github.com/helm/examples"
    gr = GitRepo(url=gr_url)
    helloworld = "charts/hello-world"
    hc = HelmChart(gr, helloworld)
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        hc.pull(tmpdir, root=helloworld)
        chart_root = Path(helloworld).parts[-1]
        assert (Path(tmpdir) / chart_root).is_dir(), f"{tree(tmpdir)}"


def test_repo_clone():
    gr_url = "https://github.com/helm/examples"
    gr = GitRepo(url=gr_url)
    helloworld = "charts/hello-world"
    with TemporaryDirectory() as tmpdir:
        gr.clone(Path(tmpdir), root=helloworld)
