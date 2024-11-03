from pathlib import Path

from pydantic import BaseModel

from deploydocus.appstate.binutils import kustomize
from deploydocus.appstate.sources import GitRepo


class Kustomization(BaseModel):
    kustomization: GitRepo | Path
    relpath: Path = Path(".")

    # def __init__(self, src: str | Path | GitRepo, relpath: str | Path | None = None):
    #     """Kustomization object
    #
    #     Args:
    #         src:
    #         relpath:
    #     """
    #     if isinstance(src, GitRepo):
    #         self.kustomization = src
    #     elif isinstance(src, str):
    #         # assume Git repo reference when it starts
    #         # with 'git+https://' or 'https://' in which case it is a url
    #         # to a git repo
    #         if src.startswith("git+"):
    #             src = src[4:]
    #         self.kustomization = GitRepo(url=AnyUrl(src))  # type: ignore[call-arg]
    #     elif isinstance(src, (Path, str)):
    #         self.kustomization = Path(src).expanduser()
    #         relpath = None  # ignore the relpath param
    #
    #     self.relpath = Path(relpath) if relpath else None

    def render(self, dst_dir: Path | str, *args) -> str:
        """

        Args:
            dst_dir: local directory to which to clone (git)
            *args: passed to git

        Returns:
            None
        """
        dst_dir = Path(dst_dir).expanduser()

        if isinstance(self.kustomization, GitRepo):
            self.kustomization.clone(dst_dir, args=args)
        ret_code, stdout, stderr = kustomize.run()
        assert ret_code == 0, (
            f"kustomization execution error " f"{ret_code=}, {stdout=}, {stderr=}"
        )
        return stdout
