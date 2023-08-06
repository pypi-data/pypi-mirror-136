from typing import Dict, List, Set, Tuple, Union

_FIELD_DICT = '_inner_dict'
_FIELD_KEY_PATH_SEPARATOR = '_key_path_separator'
_EXCLUDE_FIELDS_ = [_FIELD_DICT, _FIELD_KEY_PATH_SEPARATOR, '__len__']


class Context(object):

    def __init__(self, value_dict: Dict = None, key_path_separator='.'):
        self._key_path_separator = key_path_separator
        self._inner_dict = dict()
        if value_dict:
            self._inner_dict = self._init_config_dict(value_dict)

    def _init_config_dict(self, value_dict: Dict) -> Dict:
        config_dict = dict()
        for (k, v) in value_dict.items():
            if isinstance(v, Dict):
                config_dict[k] = Context(v, self._key_path_separator)
            elif isinstance(v, (List, Tuple, Set)):
                config_dict[k] = self._init_config_iterable(v)
            else:
                config_dict[k] = v
        return config_dict

    def _init_config_iterable(self, v: Union[List, Set, Tuple]) -> List:
        config_iterable = list()
        for sub_v in v:
            if isinstance(sub_v, Dict):
                config_iterable.append(Context(sub_v, self._key_path_separator))
            elif isinstance(sub_v, (List, Tuple, Set)):
                config_iterable.append(self._init_config_iterable(sub_v))
            else:
                config_iterable.append(sub_v)
        return config_iterable

    def __getattr__(self, key):
        if key in _EXCLUDE_FIELDS_:
            return self.__dict__[key]
        return self.__dict__[_FIELD_DICT].setdefault(key, Context(key_path_separator=self._key_path_separator))

    def __setattr__(self, key, value):
        if key in _EXCLUDE_FIELDS_:
            self.__dict__[key] = value
        else:
            if isinstance(value, Dict):
                self.__dict__[_FIELD_DICT][key] = Context(value, self._key_path_separator)
            elif isinstance(value, (List, Tuple, Set)):
                self.__dict__[_FIELD_DICT][key] = self._init_config_iterable(value)
            else:
                self.__dict__[_FIELD_DICT][key] = value

    def __bool__(self):
        return bool(self._inner_dict)

    def merge(self, another):
        from mergedeep import merge
        assert isinstance(another, Context), 'cannot merge with non-ConfigDict object'
        merged_dict = self.to_dict()
        merge(merged_dict, another.to_dict())
        return Context(merged_dict)

    def to_dict(self) -> Dict:
        value_dict = dict()
        for (k, v) in self._inner_dict.items():
            if isinstance(v, Context):
                value_dict[k] = v.to_dict()
            elif isinstance(v, (List, Tuple, Set)):
                value_dict[k] = self._to_data_list(v)
            else:
                value_dict[k] = v
        return value_dict

    def _to_data_list(self, v: Union[List, Set, Tuple]) -> List:
        data_list = list()
        for sub_v in v:
            if isinstance(sub_v, Context):
                data_list.append(sub_v.to_dict())
            elif isinstance(sub_v, (List, Tuple, Set)):
                data_list.append(self._to_data_list(sub_v))
            else:
                data_list.append(sub_v)
        return data_list

    def __getitem__(self, key: str):
        if self._key_path_separator in key:
            key_path = [t for t in key.split(self._key_path_separator) if t and t.strip()]
            config_obj = self._inner_dict
            for key_token in key_path:
                config_obj = self._getitem_ext_(config_obj, key_token)
            return config_obj

        return self._getitem_ext_(self._inner_dict, key)

    def _getitem_ext_(self, config_obj: Dict, key: str):
        key_idx = None
        if '[' in key and key[-1] == ']':
            key, key_idx = key[:-1].split('[')
        config_obj = config_obj[key]
        if key_idx and isinstance(config_obj, (List, Tuple, Set)):
            config_obj = config_obj[int(key_idx)]
        return config_obj

    def __setitem__(self, key: str, value):
        self.__setattr__(key, value)

    def __contains__(self, item):
        return item in self._inner_dict
