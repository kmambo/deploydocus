import re
from pathlib import Path
from typing import Annotated, Sequence, cast

import pydantic
from plumbum import local
from pydantic import Field, UrlConstraints, field_validator
from pydantic_core import Url

from ...binutils import git

GIT_POSTFIX = ".git"

_url_path_re = re.compile(r"/([\w-]+)/([\w-]+)(.git)?")


class NotGitRepoError(Exception): ...


GitUrl = Annotated[
    Url,
    UrlConstraints(allowed_schemes=["https", "git+https"]),
]


class GitRepo(pydantic.BaseModel):
    url: GitUrl
    branch: str | None = None
    depth: int = Field(1, gt=-1)  # type: ignore[call-arg]
    _cloned = False
    _dst_dir: Path | None = None
    _curr_branch: str | None = None

    @field_validator("url", mode="before")
    @classmethod
    def _sanitize_git_repo(cls, url: Url | str) -> GitUrl:
        if isinstance(url, str):
            url = Url(url[4:] if url.startswith("git+https") else url)
        assert url.path, f"{url=}"
        assert _url_path_re.fullmatch(url.path)
        if not url.path.rstrip("/").endswith(GIT_POSTFIX):
            url = Url(f"{url}{GIT_POSTFIX}")
        return url

    def clone(
        self,
        dst_dir: Path | str,
        args: Sequence[str] | None = None,
    ):
        """Clone the Git repo to destination directory. By default only a single
        branch is cloned.

        Args:
            dst_dir: The destination directory to clone to
            args: Additional arguments passed to `git clone`

        Returns:
            None
        """
        dst_dir = Path(dst_dir).absolute()
        if (
            self._dst_dir is not None
            and self._dst_dir.exists()
            and self._dst_dir == dst_dir
        ):  # Already cloned
            return

        dst_dir = Path(dst_dir)
        args = args or tuple()
        clone_branch_args: list[str] = []
        match self.branch, self.depth:
            case "*", 0:  # clone all branches and all depths
                pass
            case "*", _:  # clone all branches and to specified depth
                clone_branch_args.extend(
                    ["--depth", str(self.depth), "--no-single-branch"]
                )
            case None, 0:  # clone default branch
                clone_branch_args.append("--single-branch")
            case _, 0:
                clone_branch_args.extend(
                    ["--single-branch", "--branch", cast(str, self.branch)]
                )
            case None, _:
                clone_branch_args.extend(
                    ["--depth", str(self.depth), "--single-branch"]
                )
            case _, _:
                clone_branch_args.extend(
                    [
                        "--depth",
                        str(self.depth),
                        "--single-branch",
                        "--branch",
                        cast(str, self.branch),
                    ]
                )

        args = (*clone_branch_args, *args)
        clone = git["clone", *args, str(self.url), dst_dir]
        ret_code, stdout, stderr = clone.run()
        assert ret_code == 0, (
            f"git clone execution error {ret_code=}, {stdout=}," f" {stderr=}"
        )

        if self.branch is None or self.branch == "*":
            self._git_curr_branch = git["branch", "--show-branch"]
        self._cloned = True
        self._dst_dir = dst_dir

    @property
    def root(self) -> Path | None:
        return self._dst_dir

    @property
    def current_branch(self) -> str:
        if self._curr_branch is None:
            cd = local["cd"][self._dst_dir]
            gb = git["branch"]["--show-branch"]
            ret_code, stdout, stderr = gb[cd].run()
            assert ret_code == 0, (
                f"git current branch failed: {ret_code=}, {stdout=}," f" {stderr=}"
            )
            self._curr_branch = stdout.strip()
        return cast(str, self._curr_branch)
