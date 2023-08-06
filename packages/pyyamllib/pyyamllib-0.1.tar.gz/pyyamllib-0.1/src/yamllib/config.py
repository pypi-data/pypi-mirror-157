import yaml
import json
from collections.abc import MutableMapping
from typing import Dict, Any, Iterator, Set, Iterable, Union, List, Optional
from yamllib.types import PrimitiveValue
from yamllib.env import interpolate


RawValue = Union[PrimitiveValue, Dict]
YamlValue = Union[PrimitiveValue, List[PrimitiveValue], 'YamlConfig']


class YamlConfig(MutableMapping):
    def __init__(self,
                 frozen: bool = False,
                 secrets: Iterable[str] = None,
                 **kwargs: RawValue):
        """
        Recursively transforms a Python dictionary into a mutable mapping
        YamlConfig class with custom logic. This can be used as a standalone method,
        although this module is designed primarily to load YAML files. See the `.load`
        for details.

        Setting the `frozen` flag to `True` will prevent updates to the configuration object.
        This effectively disables use of the `__setitem__` and `__delitem__` methods,
        which correspond to the `config[key] = value` and `del config[key]` Python commands.

        The `secrets` field defined fields which should be obscured when displaying fields. This
        in particularly is used to protect accidentally revealing sensitive information like passwords
        when displaying the dictionary version of the config object or printing out to a string representation.
        The `secrets` should be defined as an iterable of strings, where strings can use a dot character
        to denote nesting in the config. For example, if the YAML file looks like:

        ```
        config:
          subsection:
            a: value
        ```

        you may specify `secrets=("config.subsection.a")` to obscure the `value` when using the
        `str`, `repr` or `to_dict` methods.



        :param frozen:  an optional boolean flag to note whether config can be updated
        :param secrets: fields which should be obscured when representing config object as a string or dictionary.
        :param kwargs:  the expanded dictionary of values
        """
        self.__frozen = frozen
        self.__store: Dict[str, YamlValue] = dict()
        self.__secrets: Set[str] = set(secrets) if secrets else set()

        for key, value in kwargs.items():
            if isinstance(value, dict):
                result = YamlConfig(**value)
            else:
                result = interpolate(value)
            self.__store[key] = result

    @classmethod
    def load(cls,
             path: str,
             frozen: bool = False,
             secrets: Iterable[str] = None) -> 'YamlConfig':
        """
        Loads a YAML file into a new YamlConfig object.

        :param path: the path to the YAML file to be loaded.
        :param frozen: whether or not the YamlConfig should be frozen.
        :param secrets: fields hard-coded to object as "secret" and therefore not printed in string representations.
        :return: a 'YamlConfig' object
        """
        with open(path, 'r') as f:
            config = yaml.safe_load(f.read())
        return cls(**config, frozen=frozen, secrets=secrets)

    def get(self, *keys: str, default: YamlValue = None) -> Optional[YamlValue]:
        """
        Gets a value from the config at the specified key location. Accepts any number of keys as
        non-keyword arguments, which represent nested locations in the config. For example, if the
        config has a section:
        ```
        config:
          a:
            b: value
        ```
        then get('config', 'a', 'b') returns 'value'.

        :param keys:        Keys used to access field values
        :param default:     A default value if the provided key does not exist.
        :return:            the value at the provided key location, or else the default value.
        """
        if not keys:
            raise TypeError("get expected at least 1 argument, got 0")
        key = keys[0]
        if len(keys) == 1:
            if key in self.__store:
                return self.__getitem__(keys[0])
            return default

        if key not in self.__store:
            return None
        sub_store = self.__store[keys[0]]
        return sub_store.get(*keys[1:], default=default)

    def to_dict(self, secrets: Iterable[str] = None, prefix: str = None) -> Dict[str, RawValue]:
        secrets_set: Set[str] = self.__secrets
        if secrets:
            secrets_set.update(set(secrets))

        previous_key = prefix or ''
        results = dict()
        for key, value in self.__store.items():
            current_key = f"{previous_key}.{key}" if previous_key else key
            if current_key in secrets_set:
                value = '************'
            elif isinstance(value, YamlConfig):
                value = value.to_dict(secrets=secrets_set, prefix=current_key)
            results[key] = value
        return results

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def __setitem__(self, key: str, value: YamlValue) -> None:
        if self.__frozen:
            raise AttributeError('Config is frozen. Cannot overwrite fields.')
        self.__store[key] = value
        return

    def __delitem__(self, key: str) -> None:
        if self.__frozen:
            raise AttributeError('Config is frozen. Cannot delete fields.')
        del self.__store[key]
        return

    def __getitem__(self, key: str) -> YamlValue:
        return self.__store[key]

    def __len__(self) -> int:
        return len(self.__store)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__store)
