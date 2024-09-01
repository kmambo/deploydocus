import logging
from pathlib import Path
from typing import Annotated, cast

from plumbum import local
from pydantic import AnyUrl, BaseModel, UrlConstraints, computed_field

from ..sources import GitRepo

HelmUrl = (
    Annotated[AnyUrl, UrlConstraints(allowed_schemes=["https", "oci"])]
    # | Path
)

logger = logging.getLogger(__name__)


class HelmRepoChart(BaseModel):
    url: HelmUrl

    @computed_field  # type: ignore[misc]
    @property
    def repo(self) -> HelmUrl:
        repo_path = Path(cast(str, self.url.path)).parent
        return AnyUrl.build(
            scheme=self.url.scheme,
            username=self.url.username,
            password=self.url.password,
            host=cast(str, self.url.host),
            port=self.url.port,
            path=str(repo_path),
            query=self.url.query,
            fragment=self.url.fragment,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def chart_name(self) -> str:
        return str(Path(cast(str, self.url.path)).name)


class HelmPathError(Exception):
    """Path provided not likely a help repo path."""


class HelmChartError(Exception):
    """Path could not be interpreted as a Helm chart"""


class HelmChart:
    chart: GitRepo | HelmRepoChart | Path
    relpath: Path | None

    def __init__(
        self,
        src: HelmRepoChart | GitRepo | Path | str,
        relpath: str | Path | None = None,
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
            self.relpath = Path(relpath) if relpath else None
        elif isinstance(src, str) and src[:4] == "git+":
            # with 'git+' in which case it is a url
            # to a git repo
            self.chart = GitRepo(url=AnyUrl(src[4:]))
            self.relpath = Path(relpath) if relpath else None
        elif isinstance(src, str):  # assume Helm repo reference except when it starts
            self.chart = HelmRepoChart(url=AnyUrl(src))
            self.relpath = None  # ignore the relpath param
        elif isinstance(src, (Path, str)):
            self.chart = Path(src).expanduser()
            relpath = None  # ignore the relpath param

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
                "pull", cast(HelmRepoChart, self.chart).chart_name,
                *args,
                "--repo", cast(HelmRepoChart, self.chart).repo,
                "--untar",
                "--untardir", dst_dir,
            ]
            ret_code, stdout, stderr = chart_template.run()
            assert ret_code == 0, (
                f"git clone execution error {ret_code=}, {stdout=}," f" {stderr=}"
            )
