import logging
from pathlib import Path
from typing import Annotated

import pydantic
from plumbum import local
from pydantic import AnyUrl

from ..sources import GitRepo

HelmUrl = (
    Annotated[
        pydantic.AnyUrl, pydantic.UrlConstraints(allowed_schemes=["https", "oci"])
    ]
    | Path
)

logger = logging.getLogger(__name__)


class HelmUrlModel(pydantic.BaseModel):
    url: HelmUrl


class HelmPathError(Exception):
    """Path provided not likely a help repo path."""


class HelmChartError(Exception):
    """Path could not be interpreted as a Helm chart"""


class HelmChart:
    chart: GitRepo | HelmUrl | Path
    relpath: Path | None

    def __init__(
        self, src: HelmUrl | GitRepo | Path | str, relpath: str | Path | None = None
    ):
        """
        Accepts URLs like
            - Helm chart repo assumed:
            oci://
            https://
            - git repo assumed for the following:
                - git+https://mywebsiteisagitrepo.example.com/
            - Local path assumed for the following
        The former calls helm client and the latter calls git client

        Args:
            src:
            relpath:
        """
        if isinstance(src, GitRepo):
            self.chart = src
        elif isinstance(src, str):  # assume Helm repo reference except when it starts
            # with 'git+' in which case it is a url
            # to a git repo
            self.chart = (
                HelmUrlModel(url=AnyUrl(src)).url
                if not src.startswith("git+")
                else GitRepo(url=AnyUrl(url=src[4:]))
            )
        elif isinstance(src, (Path, str)):
            self.chart = Path(src).expanduser()
            relpath = None  # ignore the relpath param

        self.relpath = Path(relpath) if relpath else None

    def pull(self, dst_dir: Path | str, *args, **kwargs) -> None:
        """

        Args:
            dst_dir: local directory to which to clone (git) or pull (helm repo)
            *args: passed to helm or git

        Returns:
            None

        Todo:
            add params to clone non-
        """
        if isinstance(dst_dir, str):
            dst_dir = Path(dst_dir).expanduser()

        if isinstance(self.chart, GitRepo):
            self.chart.clone(dst_dir, args=args, **kwargs)
        else:  # assume Helm repo ref
            helm = local["helm"]
            chart_template = helm[
                "pull", self.chart, *args, "--untar", "--untardir", dst_dir
            ]
            ret_code, stdout, stderr = chart_template.run()
            assert ret_code == 0, (
                f"git clone execution error {ret_code=}, {stdout=}," f" {stderr=}"
            )
