import importlib
import sys


def get_module(module):
    return sys.modules.get(module, importlib.import_module(module))


def get_object(module, namespace):
    module = get_module(module)
    obj = getattr(module, namespace)
    return obj


def get_instance(module, namespace, **kwargs):
    cls = get_object(module, namespace)
    return cls(**kwargs)
