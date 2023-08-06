import logging
import subprocess
import sys
from os.path import exists as path_exists
from os.path import join as path_join
from typing import Dict, Optional, Set

from .api import AddonsSuffix, OdooAddonsDef
from .git_addons import GitOdooAddons, GitSubDirOdooAddons
from .local_addons import LocalOdooAddons, LocalSubDirOdooAddons

_logger = logging.getLogger("install_addons")
_logger.setLevel(logging.INFO)


class AddonsFinder(object):
    types = [
        GitSubDirOdooAddons,
        LocalSubDirOdooAddons,
        GitOdooAddons,
        LocalOdooAddons,
    ]

    @staticmethod
    def get_addons(env_vars=None):
        # type: (Dict[str, str]) -> Set[AddonsSuffix]
        founded = {}
        for env_key in sorted(env_vars.keys()):
            addon = AddonsFinder.try_parse_key(env_key)
            if addon and env_vars.get(env_key) != str(False):
                _logger.info("Found depends %s from %s", addon, addon.identifier)
                founded[addon.identifier] = addon
        return set(founded.values())

    @staticmethod
    def _include_odoo_path(env_vars):
        # type: (Dict[str, str]) -> Dict[str, str]
        result = dict(env_vars)
        if result.get("ODOO_PATH"):
            if "ADDONS_LOCAL_SRC_ODOO_ADDONS" not in env_vars:
                result["ADDONS_LOCAL_SRC_ODOO_ADDONS"] = path_join(env_vars["ODOO_PATH"], "addons")
            if "ADDONS_LOCAL_SRC_ODOO_ADDONS_ADDONS" not in env_vars:
                result["ADDONS_LOCAL_SRC_ODOO_ADDONS_ADDONS"] = path_join(env_vars["ODOO_PATH"], "odoo", "addons")
        return result

    @staticmethod
    def parse_env(env_vars=None):
        # type: (Dict[str, str]) -> Set[OdooAddonsDef]
        env_vars = AddonsFinder._include_odoo_path(env_vars)
        return {f.extract(env_vars) for f in AddonsFinder.get_addons(env_vars)}

    @staticmethod
    def try_parse_key(env_key):
        # type: (str) -> Optional[AddonsSuffix]
        for addon_type in AddonsFinder.types:
            addons = addon_type(env_key)
            if addons.is_valid():
                _logger.info("Found depends %s from %s", addons, env_key)
                return addons
        return None


class AddonsRegistry(AddonsFinder):
    """
    Compatibility with 1.5.0
    @see AddonsFinder
    """

    def __init__(self):
        _logger.info("Depcrecated, use AddonsFinder insted. will be removed in 2.0.0")
        super(AddonsRegistry, self).__init__()


class OdooAddonsDefInstaller(OdooAddonsDef):
    def install(self):
        AddonsInstaller.install(self)


class AddonsInstaller:
    @staticmethod
    def exec_cmd(cmd, force_log=True):
        if not cmd:
            return 0
        if force_log:
            _logger.info(" ".join(cmd))
        return AddonsInstaller.exit_if_error(subprocess.Popen(cmd).wait())

    @staticmethod
    def exit_if_error(error_no):
        if error_no:
            sys.exit(error_no)
        return error_no

    @staticmethod
    def install_py_requirements(path_depot):
        path_requirements = path_join(path_depot, "requirements.txt")
        if path_exists(path_requirements):
            AddonsInstaller.exec_cmd(
                [sys.executable, "-m", "pip", "install", "-q", "--no-input", "-r", path_requirements], True
            )
        else:
            _logger.debug("No requirements.txt founded in %s", path_requirements)

    @staticmethod
    def install_npm_package(path_depot):
        path_npm = path_join(path_depot, "package.json")
        if path_exists(path_npm):
            AddonsInstaller.exec_cmd(["npm", "install", "-g", path_npm], True)
        else:
            _logger.debug("No package.json founded in %s", path_npm)

    @staticmethod
    def install(addons):
        # type: (OdooAddonsDef) -> None
        _logger.info("install %s", addons)
        try:
            for cmd in addons.install_cmd():
                AddonsInstaller.exec_cmd(cmd, True)
            AddonsInstaller.install_py_requirements(addons.addons_path)
            AddonsInstaller.install_npm_package(addons.addons_path)
        except Exception as e:
            _logger.exception("Error", exc_info=e)
            sys.exit(1)
