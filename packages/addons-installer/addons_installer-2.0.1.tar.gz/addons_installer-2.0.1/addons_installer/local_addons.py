from os.path import abspath, expanduser
from os.path import join as path_join
from typing import Dict

from .api import ABCSubDirAddons, AddonsSuffix, LocalAddonsResult


class LocalOdooAddons(AddonsSuffix):
    _prefix = "ADDONS_LOCAL"

    def __init__(self, base_key):
        # type: (str) -> None
        super(LocalOdooAddons, self).__init__("ADDONS_LOCAL", base_key)
        self.BASE_PATH = self.create_key("BASE_PATH", default="/")

    def extract(self, env_vars):
        # type: (Dict[str, str]) -> LocalAddonsResult
        res = self.to_dict(env_vars)
        return LocalAddonsResult(
            name=self.NAME.full_key,
            full_path=path_join(res[self.BASE_PATH], abspath(expanduser(res[self.NAME]))),
        )


class LocalSubDirOdooAddons(ABCSubDirAddons):
    _identifier = "ADDONS_SUBDIR_LOCAL"

    def get_parent(self, key):
        return LocalOdooAddons(key)

    def extract(self, env_vars):  # type: (Dict[str, str]) -> LocalAddonsResult
        res = self.to_dict(env_vars)
        return LocalAddonsResult(
            name=self.NAME.full_key,
            full_path=path_join(res[self.BASE_PATH], res[self.NAME]),
        )
