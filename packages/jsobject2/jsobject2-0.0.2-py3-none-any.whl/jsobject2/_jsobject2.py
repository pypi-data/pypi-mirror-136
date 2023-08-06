from typing import Generic, TypeVar, Dict, Optional

Key = TypeVar('Key')
Value = TypeVar('Value')


class JsObject(Generic[Key, Value]):
    def __init__(self, init_dict: Optional[Dict[Key, Value]] = None) -> None:
        self._data = init_dict if init_dict else {}

    def __getattr__(self, name: str) -> Optional[Value]:
        return self._data.get(name)

    def __setattr__(self, name: str, value: Value) -> None:
        if name == '_data' and '_data' not in self.__dict__:
            self.__dict__['_data'] = value
            return
        self._data[name] = value

    def __getitem__(self, key: Key) -> Optional[Value]:
        return self._data.get(key)

    def __setitem__(self, key: Key, value: Value) -> None:
        self._data[key] = value

    def __contains__(self, key: Key) -> bool:
        return key in self._data
