import inspect
from typing import TypeVar, Generic, Iterable, Any

from .generic_field import GenericField
from .utils import get_attribute, get_class_by_type, get_just_class, reduce_class_basses, is_functional_field


def _annotations_reducer(current_class):
    if current_class is Scheme:
        return

    if hasattr(current_class, '__annotations__'):
        for key, bundle in current_class.__annotations__.items():
            yield key, bundle


def _get_class_annotations(class_or_object):
    class_object = get_just_class(class_or_object)
    return reduce_class_basses(class_object, _annotations_reducer)


def _attribute_reducer(current_class, func):
    if current_class is Scheme:
        return

    for name in vars(current_class).keys():
        if name.startswith('_'):
            continue

        attr_value = getattr(current_class, name)
        result = func(name, attr_value)

        if result:
            yield result


def _has_functional_member(name, attr_value):
    if is_functional_field(attr_value):
        return name


def _own_methods_reducer(current_class):
    return _attribute_reducer(current_class, _has_functional_member)


def _get_own_methods(class_or_object):
    class_object = get_just_class(class_or_object)
    return reduce_class_basses(class_object, _own_methods_reducer)


def _has_class_member(name, attr_value):
    if isinstance(attr_value, GenericField):
        return name


def _own_class_members_reducer(current_class):
    return _attribute_reducer(current_class, _has_class_member)


def _get_own_class_members(class_or_object):
    class_object = get_just_class(class_or_object)
    return reduce_class_basses(class_object, _own_class_members_reducer)


def _proxy_method_call(method, data_object, custom_name, with_name=False):
    if with_name:
        return_value = method(data_object, custom_name)
    else:
        return_value = method(data_object)

    if type(return_value) == tuple:
        return return_value
    else:
        return return_value, custom_name


T = TypeVar('T')


class Scheme(Generic[T]):

    @classmethod
    def serialize(cls, data_object: T) -> dict[str, Any]:
        result = dict()

        annotations = _get_class_annotations(cls)
        own_methods = set(_get_own_methods(cls))
        own_class_members = set(_get_own_class_members(cls))

        for name, value_type in annotations:
            value = get_attribute(data_object, name)
            type_class = get_class_by_type(value_type)

            if issubclass(type_class, Scheme):
                result[name] = type_class.serialize(value)
            else:
                result[name] = type_class(value)

        for name in own_methods:
            method = getattr(cls, name)
            value, custom_name = _proxy_method_call(
                method,
                data_object,
                name,
                len(inspect.signature(method).parameters) == 2
            )

            result[custom_name] = value

        for name in own_class_members:
            instance = getattr(cls, name)
            value, custom_name = _proxy_method_call(instance.serialize, data_object, name, True)

            result[custom_name] = value

        return result

    @classmethod
    def serialize_array(cls, array: Iterable[T]) -> list:
        return [cls.serialize(data_object) for data_object in array]
