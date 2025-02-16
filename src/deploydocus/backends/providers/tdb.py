import threading
import typing
from pathlib import Path
from typing import Any, cast

import tinydb
from tinydb import Query

from deploydocus import AbstractK8sPkg
from deploydocus.appstate import HelmChart, Kustomization


class ManifestDict(typing.TypedDict):
    manifest_type: str
    manifest_serialized: dict[str, Any]


class AlreadyExistsError(Exception): ...


class TinyStateDb:
    """Do not instantiate directly as it is not threadsafe. Use the open_tinydb()
    function below.

    TODO: Implement locks for threaded
    """

    def __init__(self, db_filepath: Path | str):
        self.db = tinydb.TinyDB(db_filepath)

    def _manifest_type_and_rendered(
        self, manifest: dict[str, Any] | Kustomization | HelmChart | AbstractK8sPkg
    ) -> ManifestDict:
        match manifest:
            case Kustomization():
                manifest_type = "kustomization"
                manifest_serialized = cast(Kustomization, manifest).model_dump()
            case HelmChart():
                manifest_type = "helmChart"
                manifest_serialized = cast(HelmChart, manifest).model_dump()
            case AbstractK8sPkg():
                manifest_type = "package"
                manifest_serialized = cast(AbstractK8sPkg, manifest).render()
            case _:
                manifest_type = "raw"
                manifest_serialized = cast(list[dict[str, Any]], manifest)
        return {
            "manifest_type": manifest_type,
            "manifest_serialized": manifest_serialized,
        }

    def get(self, cluster_id: str, appname: str) -> dict[str, Any]:
        """

        Args:
            cluster_id:
            appname:

        Returns:

        """
        ManifestQ: Query = tinydb.Query()
        q = (ManifestQ.cluster == cluster_id) & (
            ManifestQ.appname == appname
        )  # & (ManifestQ.type == manifest_type)
        return self.db.get(q)

    def create(
        self,
        cluster_id: str,
        appname: str,
        manifest: dict[str, Any] | Kustomization | HelmChart | AbstractK8sPkg,
    ) -> Any:
        """

        Args:
            cluster_id: A unique name to identify the cluster
            appname: The name of the app (must be unique) for a manifest type
            manifest: The application manifest

        Returns:
            The document index ID
        """
        try:
            ManifestQ: Query = tinydb.Query()
            q = (ManifestQ.cluster == cluster_id) & (
                ManifestQ.appname == appname
            )  # & (ManifestQ.type == manifest_type)
            _ = self.db.search(q)[0]
            raise AlreadyExistsError(
                f"The {appname=} in cluster "
                f"{cluster_id} exists. Use update() instead."
            )
        except IndexError:
            _manifest_d = self._manifest_type_and_rendered(manifest)
            manifest_type, manifest_serialized = (
                _manifest_d["manifest_type"],
                _manifest_d["manifest_serialized"],
            )
            return self.db.insert(
                {
                    "cluster": cluster_id,
                    "appname": appname,
                    "type": manifest_type,
                    "version": 1,
                    "manifest": manifest_serialized,
                }
            )

    def update(
        self,
        cluster_id: str,
        appname: str,
        manifest: dict[str, Any] | Kustomization | HelmChart | AbstractK8sPkg,
    ):
        """Update an existing application record in th DB

        Args:
            cluster_id:
            appname:
            manifest:

        Returns:

        Raises:
            AttributeError: When there is no existing saved manifest
        """
        ManifestQ: Query = tinydb.Query()
        _manifest_d = self._manifest_type_and_rendered(manifest)
        manifest_type, manifest_serialized = (
            _manifest_d["manifest_type"],
            _manifest_d["manifest_serialized"],
        )
        q = (
            (ManifestQ.cluster == cluster_id)
            & (ManifestQ.appname == appname)
            & (ManifestQ.type == manifest_type)
        )
        idx = self.db.get(q).doc_id
        return self.db.update(
            {
                "cluster": cluster_id,
                "appname": appname,
                "type": manifest_type,
                "version": 1,
                "manifest": manifest_serialized,
            },
            doc_ids=[idx],
        )[0]


_registry = {}
_reg_lock = threading.Lock()


def open_tinydb(jsonpath: Path | str) -> TinyStateDb:
    """

    Args:
        jsonpath:

    Returns:

    """
    with _reg_lock:
        tiny_json_path = Path(jsonpath).expanduser().absolute()
        ret = _registry.get(tiny_json_path)
        if ret:
            return ret
        else:
            _registry[tiny_json_path] = TinyStateDb(jsonpath)
            return _registry[tiny_json_path]
