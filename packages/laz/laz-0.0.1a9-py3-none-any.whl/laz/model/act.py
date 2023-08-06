# std
from typing import Optional as Opt, Union

# internal
from laz.utils.errors import LazValueError
from laz.utils.contexts import in_dir
from laz.model.action import Action
from laz.model.configuration import Configuration
from laz.model.target import Target


class Act:

    def __init__(self, context: Union[Configuration, Target], action: Action):
        self.context = context
        self.action = action

    def act(self):
        self.action.run()

    @classmethod
    def new(
            cls,
            context: Union[Configuration, Target],
            action: Opt[Action] = None,
            args: Opt[str] = None,
    ):
        if action is None and args is None:
            raise LazValueError('Must provide action or args')
        if action is not None:
            return Act(context, action)
        else:
            action = Action.new(context, args)
            return Act(context, action)
