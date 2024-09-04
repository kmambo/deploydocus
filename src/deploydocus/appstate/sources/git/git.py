import re
import tempfile
from pathlib import Path
from typing import Annotated, Sequence

import pydantic
from plumbum import local
from pydantic import AfterValidator, UrlConstraints
from pydantic_core import Url

GIT_POSTFIX = ".git"

path_re = re.compile(r"/([\w-]+)/([\w-]+)")


class NotGitRepoError(Exception): ...


def _sanitize_git_repo(url: Url | str):
    if isinstance(url, str):
        url = Url(url)
    assert url.path, f"{url=}"
    assert path_re.fullmatch(url.path)
    if not url.path.endswith(GIT_POSTFIX):
        url = Url(f"{url}.git")
    return url


GitUrl = Annotated[
    Url,
    UrlConstraints(allowed_schemes=["https", "git+https"]),
    AfterValidator(_sanitize_git_repo),
]


class GitRepo(pydantic.BaseModel):
    url: GitUrl | str

    def clone(
        self,
        directory: Path | str,
        branch: str = "main",
        root: Path | str = "",
        args: Sequence[str] | None = None,
    ):
        """

        Args:
            root:
            directory:
            branch:
            args:

        Returns:

        Todo:
            Sanitize and make sure parameter root is relative only

        """
        root, directory = Path(root), Path(directory)
        with tempfile.TemporaryDirectory() as td:
            args = args or ()
            args_ext = ["--branch", branch, "--depth=1", *args]
            git = local["git"]
            clone = git["clone", *args_ext, str(self.url), td]
            ret_code, stdout, stderr = clone.run()
            assert ret_code == 0, (
                f"git clone execution error {ret_code=}, {stdout=}," f" {stderr=}"
            )

            # assert False, f"{local['ls']['-al'](td)}"
            cp = local["cp"]
            cp_recur = cp["-R"][Path(td) / root][directory]
            ret_code, stdout, stderr = cp_recur.run()
            assert ret_code == 0 and not stderr, (
                f"Recursive copy error from cloned repo: {ret_code=}, {stdout=},"
                f" {stderr=} \\n "
                f"{local['ls']['-al'][td].run()[1]}"
            )
