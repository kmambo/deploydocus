import logging
from pathlib import Path
from typing import Any

from kubernetes.client import ApiClient
from kubernetes.client.exceptions import ApiException  # type: ignore
from kubernetes.config import new_client_from_config, new_client_from_config_dict
from kubernetes.utils import FailToCreateError, create_from_dict

from deploydocus import AbstractK8sPkg
from deploydocus.installer.errors import InstallError, KubeConfigError
from deploydocus.types import K8sListModel, ManifestDict, ManifestSequence
from deploydocus.utils import (
    delete_from_dict,
    delete_from_model,
    k8s_crud_callable,
    kinds,
)

logger = logging.getLogger(__name__)


class AppNotFound(Exception): ...


def _unlist_k8s_model(x, kind: str):
    x.kind = kind
    return x


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

        Returns: The kubernetes API client

        """
        return self._api_client

    def _check_existing_k8s_objects(
        self, pkg_name: str, instance_name: str, instance_namespace: str
    ):
        for kind in reversed(kinds):
            ...

    def _install(self, component: ManifestDict, namespace: str):
        """

        Args:
            component:
            namespace:

        Returns:

        """
        component_dict: dict[str, Any] = (
            component if isinstance(component, dict) else component.to_dict()
        )
        try:
            return create_from_dict(
                k8s_client=self.api_client, data=component_dict, namespace=namespace
            )
        except FailToCreateError as e:
            logger.error(f"Failed to create {component=}")
            raise InstallError(e, component)
        except Exception:
            logger.error(f"{component_dict=}")
            raise

    def install(
        self,
        deploydocus_pkg: AbstractK8sPkg,
        installed=None,
        dry_run: bool = False,
    ) -> ManifestSequence:
        """Install the components in the defined sequence (sequence comes from
            .render() ) call. In case a component fails, the application installation
            is abandoned without rolling back the already installed components.

        Args:
            installed: (recommended) If a list is provided, the created Kubernetes
                    objects will be appended to it. This is to help track the objects
                    as they are created in the Kubernetes cluster. If
            dry_run: If dry_run is True, the objects are not created
            deploydocus_pkg: The application package to be installed

        Returns:
            sequence of components successfully installed; or in the case of
            dry_run=True, just the rendered

        Raises:
            InstallError when a component fails to be deployed.

        """
        if installed is None:
            installed = []
        try:
            components_list = deploydocus_pkg.render()
            if dry_run:
                logger.info(components_list)
                return components_list
            for component in components_list:
                installed_component = self._install(
                    component,
                    namespace=deploydocus_pkg.instance_settings.instance_namespace,
                )
                logger.debug(f"{installed_component=}")
                installed.extend(installed_component)
        except InstallError:
            logger.error(
                "Installation failed: "
                f"package={deploydocus_pkg.pkg_name} "
                f"instance name={deploydocus_pkg.instance_settings}"
            )
            raise

        return installed

    def uninstall(
        self,
        deploydocus_pkg: AbstractK8sPkg,
    ) -> ManifestSequence:
        """Uninstall a package.

        Args:
            deploydocus_pkg: The package to install
            instance_settings: The instance settings used to instantiate the package

        Returns:

        """
        uninstalled = []

        components_list = self.find_current_app_installations(deploydocus_pkg)
        for component in reversed(components_list):
            ret = delete_from_dict(
                self.api_client,
                data=component,
                namespace=deploydocus_pkg.instance_settings.instance_namespace,
            )

            if ret:
                uninstalled.extend(ret)
        return uninstalled

    def revert_install(
        self, installed: ManifestSequence, namespace: str, uninstall_point=0
    ) -> ManifestSequence:
        """Reverse an installation

        Args:
            namespace:
            installed:
            uninstall_point:

        Returns:

        """
        uninstalled = []
        for component in reversed(installed[uninstall_point:]):
            logger.info(f"Reverting: {component}")
            ret = (
                delete_from_dict(
                    self.api_client,
                    data=component,
                    namespace=namespace,
                )
                if isinstance(component, dict)
                else delete_from_model(
                    self.api_client,
                    data=component,
                    namespace=namespace,
                )
            )

            if ret:
                uninstalled.append(ret)
        return uninstalled

    def find_current_app_installations(
        self,
        deploydocus_pkg: AbstractK8sPkg,
    ) -> ManifestSequence:
        """Look for installed versions of the application

        Args:
            deploydocus_pkg:

        Returns:

        """
        # TODO: expand  deploydocus_pkg to accept just application name
        #  and namespace as a dict
        selectors = ",".join(
            [f"{k}={v}" for k, v in deploydocus_pkg.default_selectors.items()]
        )
        existing_components: list[ManifestDict] = []
        for kind in kinds:
            try:
                if kind[-4:] == "List":
                    continue
                _callable, _namespaced = k8s_crud_callable(
                    k8s_client=self.api_client, op="list", kind=kind
                )

                _components: K8sListModel = (
                    _callable(
                        namespace=deploydocus_pkg.instance_settings.instance_namespace,
                        label_selector=selectors,
                    )
                    if _namespaced
                    else _callable(label_selector=selectors)
                )
                logger.info(f"{_components=}")
                if _components.items:
                    items = [_unlist_k8s_model(i, kind) for i in _components.items]
                    existing_components.extend(items)
            except TypeError as t:
                raise Exception(f"{kind=}") from t
            except ApiException as ae:
                if ae.status == 404:
                    continue
                logger.error(f"{kind=} {ae.status=} {ae.reason=} {ae.body=}")
                raise

        return existing_components

    def upgrade_current_installation(
        self, deploydocus_pkg: AbstractK8sPkg, create_allowed=True
    ):
        """Upgrade an existing installation. If there is none, then (optionally),
        install

        Args:
            create_allowed: If True, create a new
            deploydocus_pkg:

        Returns:

        """
        current = self.find_current_app_installations(deploydocus_pkg)
        if not current and not create_allowed:
            raise AppNotFound
        elif not current and create_allowed:
            self.install(deploydocus_pkg)


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
