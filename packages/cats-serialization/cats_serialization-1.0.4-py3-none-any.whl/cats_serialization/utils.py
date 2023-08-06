import inspect
import sys
from inspect import isclass
from typing import Generic


def get_just_class(class_or_object):
    return class_or_object if hasattr(class_or_object, '__bases__') else class_or_object.__class__


def reduce_class_basses(class_object, func):
    yield from func(class_object)

    if not class_object.__bases__:
        return

    for base in class_object.__bases__:
        yield from reduce_class_basses(base, func)


def get_attribute(data_object, name):
    if not name:
        return data_object
    elif type(data_object) == dict:
        return data_object.get(name)
    else:
        return getattr(data_object, name)


def get_class_by_type(class_type):
    module = sys.modules[class_type.__module__]
    return getattr(module, class_type.__name__)


def is_functional_field(attr_value):
    if inspect.ismethod(attr_value):
        return isclass(attr_value.__self__) and attr_value.__self__ is not Generic
    else:
        return inspect.isfunction(attr_value)
