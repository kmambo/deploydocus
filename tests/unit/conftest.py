from typing import Generator

import pytest
from pydantic import AnyUrl

from deploydocus.appstate.helm3 import HelmChart
from deploydocus.appstate.sources import GitRepo


@pytest.fixture
def helm_charts() -> Generator[tuple[GitRepo, str, str, HelmChart], None, None]:
    yield (
        GitRepo(url=AnyUrl("https://github.com/helm/examples")),
        "oci://registry-1.docker.io/bitnamicharts/mariadb",
        "https://owkin.github.io/charts/pypiserver",
        HelmChart(""),
    )
