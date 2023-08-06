# std
from typing import List, Optional as Opt

# internal
from laz.utils.errors import LazValueError
from laz.utils.contexts import in_dir
from laz.model.action import Action
from laz.model.target import Target


class Act:

    def __init__(self, target: Target, action: Action):
        self.target = target
        self.action = action

    def act(self):
        with in_dir(self.target.data['dirpath']):
            self.action.run()

    @classmethod
    def new(cls, target: Target, action: Opt[Action] = None, args: Opt[str] = None):
        if action is None and args is None:
            raise LazValueError('Must provide action or args')
        if action is not None:
            return Act(target, action)
        else:
            action = Action.new(target, args)
            return Act(target, action)
