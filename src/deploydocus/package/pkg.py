import abc
import logging
from functools import wraps
from pathlib import Path
from typing import LiteralString

from deploydocus.package.settings import InstanceSettings
from deploydocus.package.types import (
    SUPPORTED_KINDS,
    LabelsDict,
    LabelsSelector,
    ManifestSequence,
)

logger = logging.getLogger(__name__)

DEPLOYDOCUS_DOMAIN: LiteralString = "deploydocus.io"


def autosort(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        ret: ManifestSequence = f(*args, **kwargs)
        ret.sort(
            key=lambda obj: list(SUPPORTED_KINDS).index(
                obj["kind"] if isinstance(obj, dict) else obj.kind
            )
        )
        return ret

    print(type(f))

    return wrapped


class AbstractK8sPkg(abc.ABC):
    pkg_name: str
    pkg_version: str

    def __init__(
        self,
        instance: InstanceSettings,
        *,
        pkg_version: str,
        pkg_name: str | None = None,
    ):
        """

        Args:
            pkg_name:
            pkg_settings_class:
        """
        assert pkg_version.strip(), "parameter pkg_version cannot be empty or None"
        self.pkg_name = pkg_name or self.__class__.__name__.lower()
        self.pkg_version = pkg_version
        self.instance_settings = instance

    @property
    def default_labels(self) -> LabelsDict:
        return {
            "app.kubernetes.io/name": self.pkg_name,
            "app.kubernetes.io/instance": self.instance_settings.instance_name,
            "app.kubernetes.io/version": self.instance_settings.instance_version,
            "app.kubernetes.io/managed-by": DEPLOYDOCUS_DOMAIN,
            "deploydocus-pkg": f"{self.pkg_name}-{self.pkg_version}",
        }

    @property
    def default_selectors(self) -> LabelsSelector:
        return {
            "app.kubernetes.io/name": self.pkg_name,
            "app.kubernetes.io/instance": self.instance_settings.instance_name,
            "app.kubernetes.io/managed-by": DEPLOYDOCUS_DOMAIN,
        }

    def read_template(self, template_filename: str, **kwargs) -> str:
        """

        Args:
            template_filename:
            **kwargs:

        Returns:

        """
        pwd = Path(__file__).parent
        with open(pwd / template_filename, "rt") as f:
            full_file_template = f.read()
        return full_file_template.format(**kwargs)

    @abc.abstractmethod
    def render(self) -> ManifestSequence:
        """Renders (as JSON or YAML) the application

        Returns:

        """
        ...
