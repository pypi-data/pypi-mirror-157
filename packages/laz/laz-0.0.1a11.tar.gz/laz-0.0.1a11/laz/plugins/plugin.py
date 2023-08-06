# std
from typing import List, Union

# internal
from laz.utils import log
from laz.model.configuration import Configuration
from laz.model.target import Target


class Plugin:
    context: Union[Configuration, Target]

    def __init__(self, context: Union[Configuration, Target]):
        self.context = context

    def __init_subclass__(cls, **kwargs):
        PLUGINS.append(cls)
        cls.before_all = log_method(cls.before_all)
        cls.before_target = log_method(cls.before_target)
        cls.after_target = log_method(cls.after_target)
        cls.after_all = log_method(cls.after_all)

    def before_all(self):
        raise NotImplementedError

    def before_target(self):
        raise NotImplementedError

    def after_target(self):
        raise NotImplementedError

    def after_all(self):
        raise NotImplementedError


def log_method(method):
    class_name = method.__qualname__.split('.')[0]
    def wrapper(self, *args, **kwargs):
        if class_name != 'Plugin':
            log.debug(f'Running {self.__class__.__name__} {method.__name__}')
        return method(self, *args, **kwargs)
    return wrapper


PLUGINS: List[type(Plugin)] = []
