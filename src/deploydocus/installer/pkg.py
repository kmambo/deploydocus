import abc
import logging
from pathlib import Path
from typing import Any

from kubernetes.client import ApiClient
from kubernetes.config import new_client_from_config, new_client_from_config_dict
from kubernetes.utils import FailToCreateError, create_from_dict

from ..utils import delete_from_dict
from .errors import InstallError, KubeConfigError
from .settings import InstanceSettings, PkgSettings
from .types import ManifestDict, ManifestSequence

logger = logging.getLogger(__name__)


def _only_one(
    context: str | None = None,
    config_file: Path | None = None,
    config_dict: dict[str, Any] | None = None,
) -> ApiClient:
    match (config_dict, context, config_file):
        case (None, _, _):
            return new_client_from_config(
                config_file=config_file, context=context, persist_config=False
            )
        case (_, _, None):
            return new_client_from_config_dict(
                config_dict=config_dict, context=context, persist_config=False
            )
        case _, _, _:
            raise KubeConfigError("Both config_file and config_dict cannot be provided")


class AbstractK8sPkg(abc.ABC):
    deploydocus_domain: str = "deploydocus.io"
    pkg_name: str
    pkg_settings: PkgSettings

    def __init__(
        self,
        pkg_name: str | None = None,
        pkg_settings_class: type[PkgSettings] = PkgSettings,
    ):
        """

        Args:
            pkg_name:
            pkg_settings_class:
        """
        self.pkg_name = pkg_name or self.__class__.__name__
        self.pkg_settings = pkg_settings_class()

    @property
    def namespace(self):
        return self.pkg_settings.pkg_namespace

    def default_selectors(self, **kwargs) -> dict[str, str]:
        pkg_name, pkg_version = (
            kwargs.get("pkg_name") or self.pkg_settings.pkg_name,
            kwargs.get("pkg_version") or self.pkg_settings.pkg_version,
        )
        return {
            "app.kubernetes.io/name": pkg_name,
            "app.kubernetes.io/instance": pkg_version,
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
    def render(self, settings: InstanceSettings, **kwargs) -> ManifestSequence:
        """Renders (as JSON or YAML) the application

        Args:
            settings:
            **kwargs:

        Returns:

        """
        ...


class PkgInstaller:
    """
    Take a concrete instance of a
    """

    _api_client: ApiClient

    def __init__(
        self,
        context: str | None = None,
        config_file: Path | None = None,
        config_dict: dict[str, Any] | None = None,
    ):
        self._api_client = _only_one(
            context=context, config_dict=config_dict, config_file=config_file
        )

    @property
    def api_client(self) -> ApiClient:
        """

        Returns: The kubernetes

        """
        return self._api_client

    def _install(self, component: ManifestDict, namespace: str):
        component_dict: dict[str, Any] = (
            component if isinstance(component, dict) else component.to_dict()
        )
        try:
            return create_from_dict(
                k8s_client=self.api_client, data=component_dict, namespace=namespace
            )
        except FailToCreateError as e:
            logger.error(f"Failed to create {component=}")
            raise InstallError(e)
        except Exception:
            logger.exception(f"{component_dict=}")
            raise

    def install(
        self,
        deploydocus_pkg: AbstractK8sPkg,
        instance_settings: InstanceSettings,
        dry_run: bool = False,
    ) -> ManifestSequence:
        """Install the components in the defined sequence (sequence comes from
            .render() ) call

        Args:
            dry_run:
            instance_settings:
            deploydocus_pkg:

        Returns:
            sequence of components successfully installed; or in the case of
            dry_run=True, just the rendered

        """
        installed = []
        try:
            components_list = deploydocus_pkg.render(instance_settings)
            if dry_run:
                logger.info(components_list)
                return components_list
            for component in components_list:
                status = self._install(
                    component, namespace=instance_settings.instance_namespace
                )
                logger.debug(f"{status=}")
                installed.append(status)
        except InstallError:
            logger.exception(
                "Installation failed: "
                f"package={deploydocus_pkg.pkg_name} "
                f"instance name={instance_settings}"
            )

        return installed

    def uninstall(
        self,
        deploydocus_pkg: AbstractK8sPkg,
        instance_settings: InstanceSettings,
    ) -> ManifestSequence:
        uninstalled = []
        components_list = deploydocus_pkg.render(instance_settings)
        for component in reversed(components_list):
            ret = delete_from_dict(
                self.api_client,
                data=component,
                namespace=instance_settings.instance_namespace,
            )

            if ret:
                uninstalled.append(ret)
        return uninstalled
