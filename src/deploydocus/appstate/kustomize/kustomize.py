from pathlib import Path

from pydantic import AnyUrl

from deploydocus.appstate.sources import GitRepo


class Kustomization:
    kustomization: GitRepo | Path
    relpath: Path | None

    def __init__(self, src: str | Path | GitRepo, relpath: str | Path | None = None):
        if isinstance(src, GitRepo):
            self.kustomization = src
        elif isinstance(src, str) and src.startswith("git+"):
            # assume Git repo reference when it starts
            # with 'git+' in which case it is a url
            # to a git repo
            self.kustomization = GitRepo(url=AnyUrl(src[4:]))
        elif isinstance(src, (Path, str)):
            self.kustomization = Path(src).expanduser()
            relpath = None  # ignore the relpath param

        self.relpath = Path(relpath) if relpath else None

    def pull(self, dst_dir: Path | str, *args, **kwargs):
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

        if isinstance(self.kustomization, GitRepo):
            self.kustomization.clone(dst_dir, args=args, **kwargs)
