# std
from __future__ import annotations
from abc import abstractmethod
import os
import subprocess
from typing import List, Optional as Opt, Union

# internal
from laz.utils.errors import LazValueError
from laz.utils import log
from laz.utils.types import Data, DictData, ListData
from laz.model.target import Target


class Action:
    action_types = []

    def __init__(self, target: Target, run_data: Data):
        self.target: Target = target
        self.run_data: Data = run_data

    def __init_subclass__(cls):
        if cls.__name__ != 'ShellAction':
            cls.action_types.append(cls)

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        raise NotImplementedError

    @classmethod
    def new(cls, target: Target, run_data: Data) -> Action:
        for action_type in cls.action_types:
            if action_type.is_handler(target, run_data):
                return action_type.new(target, run_data)
        if ShellAction.is_handler(target, run_data):
            return ShellAction.new(target, run_data)
        cls.raise_value_error(target, run_data)

    @classmethod
    def raise_value_error(cls, target: Target, run_data: Data, msg: Opt[str] = None):
        log.error(f'target -> {target.serialize()}')
        log.error(f'run data -> {run_data}')
        msg = msg or f'Given values could not be handled as a {cls.__name__}'
        raise LazValueError(msg)


class DefaultAction(Action):

    def run(self):
        raise NotImplementedError

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        if isinstance(run_data, str) and run_data == 'default':
            return True
        else:
            return False

    @classmethod
    def new(cls, target: Target, run_data: Data) -> Action:
        configured_actions: DictData = target.data.get('actions', {})
        if isinstance(run_data, str) and run_data in configured_actions:
            return Action.new(target, configured_actions[run_data])
        else:
            cls.raise_value_error(target, run_data, 'No default action found')


class ConfiguredAction(Action):

    def run(self):
        raise NotImplementedError

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        configured_actions: DictData = target.data.get('actions', {})
        if isinstance(run_data, str) and run_data in configured_actions:
            return True
        else:
            return False

    @classmethod
    def new(cls, target: Target, run_data: Data) -> Action:
        configured_actions: DictData = target.data.get('actions', {})
        if isinstance(run_data, str) and run_data in configured_actions:
            return Action.new(target, configured_actions[run_data])
        else:
            cls.raise_value_error(target, run_data)


class MultipleActions(Action):

    def __init__(self, target: Target, run_data: ListData):
        super().__init__(target, run_data)
        self.actions = [Action.new(target, d) for d in self.run_data]

    def run(self):
        results = []
        for action in self.actions:
            results.append(action.run())
        return results

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        return isinstance(run_data, list)

    @classmethod
    def new(cls, target: Target, run_data: ListData) -> Action:
        return MultipleActions(target, run_data)


class ConditionalAction(Action):

    def run(self):
        result = Action.new(self.target, self.run_data['condition']).run()
        if bool(result):
            if 'if' in self.run_data:
                return Action.new(self.target, self.run_data['if']).run()
        else:
            if 'else' in self.run_data:
                return Action.new(self.target, self.run_data['else']).run()

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        return isinstance(run_data, dict) and 'condition' in run_data

    @classmethod
    def new(cls, target: Target, run_data: DictData) -> Action:
        return cls(target, run_data)


class SwitchAction(Action):

    def run(self):
        result = Action.new(self.target, self.run_data['switch']).run()
        if result in self.run_data:
            return Action.new(self.target, self.run_data[result]).run()
        elif 'default' in self.run_data:
            return Action.new(self.target, self.run_data['default']).run()
        else:
            return

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        return isinstance(run_data, dict) and 'switch' in run_data

    @classmethod
    def new(cls, target: Target, run_data: DictData) -> Action:
        return cls(target, run_data)


class ShellAction(Action):
    run_data: DictData

    def run(self):
        env = {
            **os.environ,
            **self.target.data.get('env', {}),
        }
        if self.run_data.get('capture'):
            type_str = self.run_data.get('type', 'str')
            result = subprocess.run(self.args(), env=env, capture_output=True).stdout.decode()
            if self.run_data.get('strip', True):
                result = result.strip()
            result = eval(f'{type_str}({result})')
            return result
        else:
            return subprocess.run(self.args(), env=env).returncode == 0

    def args(self) -> List[str]:
        return [self._shell(), '-c', self.run_data['command']]

    def _shell(self) -> str:
        return os.environ.get('SHELL', 'bash')

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        if isinstance(run_data, str):
            return True
        elif isinstance(run_data, dict) and 'command' in run_data:
            return True
        else:
            cls.raise_value_error(target, run_data)

    @classmethod
    def new(cls, target: Target, run_data: Union[str, DictData]) -> Action:
        if isinstance(run_data, str):
            run_data = {'command': run_data}
        return cls(target, run_data)


class PythonAction(Action):

    def run(self):
        return eval(self.run_data['python'])

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        return isinstance(run_data, dict) and 'python' in run_data

    @classmethod
    def new(cls, target: Target, run_data: DictData) -> Action:
        return cls(target, run_data)
