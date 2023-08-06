import abc
import sys
from typing import Dict, List, Optional

if sys.version_info[0] == 2:  # Python 2

    class ABC(object):
        __meta_class__ = abc.ABCMeta
        __slots__ = ()

else:
    ABC = abc.ABC


class KeySuffix(object):
    def __init__(self, addons, name, default=None, have_default=True):
        # type: (AddonsSuffix, str, str, bool) -> KeySuffix
        self.name = name
        self.prefix = addons.prefix
        self.base_key = addons.identifier
        self.default_value = default
        self.have_default = have_default

    def get_value(self, env_vars, with_default=True):
        return (
            env_vars.get(self.full_key, env_vars.get(self.default_key, with_default and self.default_value or None))
            or None
        )

    def get_key(self, *args):
        # type: (List[str]) -> str
        return "_".join([s for s in args if s]).upper()

    @property
    def full_key(self):
        return self.get_key(self.prefix, self.base_key, self.name)

    @property
    def default_key(self):  # type: ()-> Optional[str]
        return self.have_default and self.get_key(self.prefix, AddonsSuffix.ADDONS_DEFAULT, self.name) or None

    def __repr__(self):
        return "%s(%s, default=%s)" % (type(self).__name__, self.full_key, self.default_key)


class AddonsSuffix(ABC):
    ADDONS_DEFAULT = "DEFAULT"
    ADDONS_SUFFIX_EXCLUDE = "EXCLUDE"

    def __init__(self, prefix, base_key):
        # type: (str, str) -> AddonsSuffix
        super(AddonsSuffix, self).__init__()
        self.base_key = base_key
        self.prefix = prefix
        self._key_registry = {}
        self._values = {}
        self.NAME = self.create_key("", have_default=False)

    @property
    def identifier(self):
        return self.base_key.replace(self.prefix, "").strip("_")

    def extract(self, env_vars):
        # type: (Dict[str, str]) -> OdooAddonsDef
        raise NotImplementedError()

    def to_dict(self, env_vars):
        # type: (Dict[str, str]) -> Dict[KeySuffix, str]
        return {key: key.get_value(env_vars) for key_name, key in self._key_registry.items()}

    def get_suffix_keys(self):
        # type: () -> List[str]
        return list(self._key_registry.keys())

    def create_key(self, name, default=None, have_default=True):
        key = KeySuffix(addons=self, name=name, default=default, have_default=have_default)
        self._key_registry[name] = key
        return key

    def is_valid(self):
        return (
            self.base_key.startswith(self.prefix)
            and self.identifier != self.base_key
            and not any(self.base_key.endswith(suffix) for suffix in self.get_suffix_keys() if suffix)
            and not self.base_key.endswith(self.ADDONS_SUFFIX_EXCLUDE)
        )

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self.identifier)

    def __eq__(self, other):
        return isinstance(other, AddonsSuffix) and other.identifier == self.identifier

    def __hash__(self):
        return hash(self.identifier)


class OdooAddonsDef(ABC):
    def __init__(self, name):
        self.name = name

    @property
    def addons_path(self):
        raise NotImplementedError()

    def install_cmd(self):
        # type: () -> List[List[str]]
        raise NotImplementedError()

    def arg_cmd(self):
        # type: () -> List[str]
        raise NotImplementedError()


class ABCSubDirAddons(AddonsSuffix, ABC):
    _identifier = None

    def __init__(self, base_key):
        of_ref = base_key.split("_OF_")[-1]
        super(ABCSubDirAddons, self).__init__(self._identifier, base_key)
        self.parent_addons = None
        if of_ref and self.is_valid():
            tmp = self.get_parent("")
            key_git = tmp.prefix + "_" + of_ref
            self.parent_addons = self.get_parent(key_git)
            assert self.parent_addons.is_valid(), "The key %s is not a Addons valid key" % key_git

    def get_parent(self, key):
        raise NotImplementedError

    def extract(self, env_vars):  # type: (Dict[str, str]) -> LocalAddonsResult
        raise NotImplementedError


class LocalAddonsResult(OdooAddonsDef):
    def install_cmd(self):
        return []

    def arg_cmd(self):
        return []

    @property
    def addons_path(self):
        return self.full_path

    def __init__(self, name, full_path):
        super(LocalAddonsResult, self).__init__(name)
        self.name = name
        self.full_path = full_path
