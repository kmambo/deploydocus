from deploydocus.appstate.helm3.helm import HelmRepoChart


def test_helmchart_repo_oci(helm_repo_charts):
    chart = HelmRepoChart(url=helm_repo_charts[1])
    assert (
        str(chart.repo) == "oci://registry-1.docker.io/bitnamicharts"
    ), f"{chart.repo=}"
    assert str(chart.chart_name) == "mariadb", f"{chart.chart_name}"


def test_helmchart_repo_https(helm_repo_charts):
    chart = HelmRepoChart(url=helm_repo_charts[2])
    assert str(chart.repo) == "https://owkin.github.io/charts", f"{chart.repo=}"
    assert str(chart.chart_name) == "pypiserver", f"{chart.chart_name=}"
