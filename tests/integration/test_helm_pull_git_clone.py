from plumbum import local

from deploydocus import HelmChartGitRepo
from deploydocus.appstate.helm3 import HelmRepoChart
from deploydocus.appstate.sources import GitRepo

ls = local["ls"]


def test_helm_from_gitrepo():
    hc = HelmChartGitRepo(
        url=GitRepo(
            url="git+https://github.com/kmambo/deploydocus-companion.git",
            branch="add_oci_kafka_chart",
            depth=1,
        ),
        relpath="kafka-helm-chart-inside/kafka-chart",
    )
    _: str = hc.render()


def test_helmrepo_pull_https(helm_repo_chart_url_https):
    hc = HelmRepoChart(url=helm_repo_chart_url_https)
    release_name = "my-release"
    _: str = hc.render(release_name)
    # TODO:  what should I do with the manifest


def test_helmrepo_pull_oci(helm_repo_chart_url_oci):
    hc = HelmRepoChart(url=helm_repo_chart_url_oci)
    release_name = "my-release"
    _: str = hc.render(release_name)
    # TODO:  what should I do with the manifest
