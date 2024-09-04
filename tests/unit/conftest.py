from typing import Generator

import pytest
from pydantic import AnyUrl

from deploydocus.appstate.sources import GitRepo


@pytest.fixture
def helm_repo_charts() -> Generator[tuple[GitRepo, str, str], None, None]:
    yield (
        GitRepo(url=AnyUrl("https://github.com/helm/examples")),
        "oci://registry-1.docker.io/bitnamicharts/mariadb",
        "https://owkin.github.io/charts/pypiserver",
    )
