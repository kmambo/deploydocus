from pathlib import Path

from pydantic import BaseModel

from deploydocus.appstate.binutils import kustomize
from deploydocus.appstate.sources import GitRepo


class Kustomization(BaseModel):
    kustomization: GitRepo | Path
    relpath: Path = Path(".")

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
