from pathlib import Path
from tempfile import TemporaryDirectory

from plumbum import local

from deploydocus.appstate.kustomize import Kustomization
from deploydocus.appstate.sources import GitRepo


def test_kustomize_pull_git():
    gr_url = "https://github.com/kubernetes-sigs/kustomize.git"
    gr = GitRepo(url=gr_url)
    helloworld = "examples/helloWorld"
    kustomize_repo = Kustomization(gr, helloworld)
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        kustomize_repo.pull(tmpdir, root=helloworld, branch="master")
        kustomize_relative_root = Path(helloworld).parts[-1]
        assert (
            Path(tmpdir) / kustomize_relative_root / "kustomization.yaml"
        ).is_file(), f"{tree(tmpdir)}"
