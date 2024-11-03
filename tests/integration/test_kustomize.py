from pathlib import Path
from tempfile import TemporaryDirectory

from plumbum import local

from deploydocus.appstate.kustomize import Kustomization
from deploydocus.appstate.sources import GitRepo


def test_kustomize_pull_git():
    gr_url = "https://github.com/kmambo/deploydocus-companion.git"
    gr = GitRepo(url=gr_url, branch="add_oci_kafka_chart")
    relpath = "kubebuilder-kustomization-inside/config/manifests"
    kustomize_repo = Kustomization(kustomization=gr, relpath=relpath)
    tree = local["tree"]
    with TemporaryDirectory() as tmpdir:
        kustomize_repo.render(tmpdir)
        assert (
            Path(tmpdir) / relpath / "kustomization.yaml"
        ).is_file(), f"{tree(tmpdir)}"
