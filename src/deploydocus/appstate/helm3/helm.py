import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Any, Mapping, Sequence, cast

import yaml
from pydantic import (
    AnyUrl,
    BaseModel,
    Field,
    UrlConstraints,
    computed_field,
    field_validator,
)

from ..binutils import helm
from ..sources import GitRepo, GitUrl

HelmUrl = Annotated[AnyUrl, UrlConstraints(allowed_schemes=["https", "oci"])]

HELM_REPO_PREFIXES = ("https://", "oci://")

logger = logging.getLogger(__name__)


class HelmPathError(Exception):
    """Path provided not likely a help repo path."""


class HelmChartError(Exception):
    """Path could not be interpreted as a Helm chart"""


class HelmConfigGitRepo:
    helm_config: GitRepo  # | Path | Mapping[str, Any]
    _dst_dir: Path | None = None

    def pull(
        self,
        dst_dir: str | Path,
    ):
        """Clone the repo and copy the helm config files.

        Args:
            dst_dir: The destination directory into which the HelmConfig files
                are created

        Returns:

        """
        assert (
            self._dst_dir is None
        ), "HelmConfig source already pulled and should not be re-pulled"
        dst_dir = Path(dst_dir)
        self.helm_config.clone(dst_dir)
        self._dst_dir = dst_dir

    def config(
        self, filepath: Path | str
    ) -> Mapping[str, Any] | Sequence[Mapping[str, Any]]:
        filepath = Path(filepath)
        with open(filepath, "rt") as f:
            return yaml.safe_load(f)


class HelmRender:
    def render(
        self,
        release_name: str | None = None,
        namespace: str = "default",
        configs: Sequence[HelmConfigGitRepo] | None = None,
        *args,
    ) -> str:
        helm_template = helm["template"]
        if release_name is not None:
            helm_template = helm_template[release_name]
        helm_template = helm_template[*args]
        if namespace != "default":
            helm_template = helm_template["-n"][namespace]
        ret_code, stdout, stderr = helm_template.run()
        assert ret_code == 0, f"Helm render error {ret_code=}, {stdout=}," f" {stderr=}"

        return stdout


class HelmRepoChart(BaseModel):
    """Represents a chart from a Helm Repo (but not a Git repo)"""

    url: HelmUrl
    version: str | None = None

    def render(
        self,
        release_name: str | None = None,
        configs: Sequence[HelmConfigGitRepo] | None = None,
        *args,
    ) -> str:
        """

        Args:
            release_name:
            configs:
            *args:

        Returns:

        """
        helm_template = helm["template"]
        if release_name is not None:
            helm_template = helm_template[release_name]
        helm_template = helm_template[*self.template_cmd, *args]
        ret_code, stdout, stderr = helm_template.run()
        assert ret_code == 0, f"Helm render error {ret_code=}, {stdout=}," f" {stderr=}"

        return stdout

    @computed_field  # type: ignore[misc]
    @property
    def repo(self) -> HelmUrl:
        repo_path = str(Path(cast(str, self.url.path)).parent)[1:]
        return AnyUrl.build(
            scheme=self.url.scheme,
            username=self.url.username,
            password=self.url.password,
            host=cast(str, self.url.host),
            port=self.url.port,
            path=repo_path,
            query=self.url.query,
            fragment=self.url.fragment,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def chart_name(self) -> str:
        return str(Path(cast(str, self.url.path)).name)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def template_cmd(self) -> Sequence[str]:
        return (
            [self.chart_name, f"--repo={self.repo}"]
            if self.url.scheme == "https"
            else [str(self.url)]
        )


class HelmChartGitRepo(BaseModel):
    git_repo: GitRepo = Field(alias="url")
    relpath: Path | str = Path(".")

    @field_validator("git_repo", mode="before")
    @classmethod
    def _git_repo_src(cls, value: GitUrl | GitRepo) -> GitRepo:
        return value if isinstance(value, GitRepo) else GitRepo(url=value)

    @field_validator("relpath", mode="before")
    @classmethod
    def _relative_path(cls, value: Path | str) -> Path:
        return value if isinstance(value, Path) else Path(value)

    def render(
        self,
        release_name: str | None = None,
        namespace: str = "default",
        create_namespace=False,
        configs: Sequence[HelmConfigGitRepo] | None = None,
        gitargs: Sequence[str] | None = None,
        *args,
    ) -> str:
        """
        Calls `helm template [NAME] [CHART] --dry-run=server

        Args:
            create_namespace: If True, create the namespace if not present
                (note: may fail if you don't have sufficient permission to create
                a namespace)
            namespace: The namespace to pass to the helm command as
                "-n <namespace>"
            gitargs: Parameters passed to `git` to be used for cloning.
            release_name: If present, this is the application name.
            configs: values file paths or values to use
            *args: passed to helm and should be be all str.
                Must not have "dry-run=", "--repo" entry

        Returns:
            The rendered chart

        """

        helm_template = helm["template"]
        if release_name is not None:
            helm_template = helm_template[release_name]

        with TemporaryDirectory() as td:
            self.git_repo.clone(td, args=gitargs)

            chart_path = Path(td) / self.relpath
            helm_template_cmd = helm_template[chart_path][*args]
            ret_code, stdout, stderr = helm_template_cmd.run()
            assert (
                ret_code == 0
            ), f"helm execution error {ret_code=}, {stdout=}, {stderr=}"

            return stdout


HelmChart = HelmChartGitRepo | HelmRepoChart
