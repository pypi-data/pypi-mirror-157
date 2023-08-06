from inspect import isfunction, ismethod
from typing import TypeVar, Any, Callable

from .generic_field import GenericField
from .scheme import Scheme
from .utils import get_attribute


T = TypeVar('T')


class BasicField(GenericField[T]):

    def __init__(self, key: str = None, custom_name: str = None):
        self._key = key
        self._custom_name = custom_name

    def _map_element(self, data_object: T, key: str | None = None):
        return get_attribute(data_object, self._key or key)

    def serialize(self, data_object: T, key: str | None = None) -> Any:
        mapped_value = self._map_element(data_object, key)
        custom_name = self._custom_name or key

        return (mapped_value, custom_name) if custom_name else mapped_value


def _basic_mapper(element):
    return element


MapperType = Callable[[Any], Any] | GenericField | Scheme


class MappedField(BasicField[T]):

    def __init__(self, mapper: MapperType = _basic_mapper, **kwargs):
        super().__init__(**kwargs)

        self._mapper = mapper if (isfunction(mapper) or ismethod(mapper)) else mapper.serialize

    def _map_element(self, data_object: T, key: str | None = None):
        return self._mapper(super()._map_element(data_object, key))


class IterableField(MappedField[T]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _map_element(self, data_object: T, key: str | None = None):
        iterable = get_attribute(data_object, self._key or key)
        return [self._mapper(e) for e in iterable]
