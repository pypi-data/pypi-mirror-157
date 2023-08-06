# internal
from laz.plugins.plugin import Plugin


class TerraformPlugin(Plugin):

    @property
    def config(self) -> dict:
        return self.context.data.get('terraform', {})

    @property
    def hooks(self) -> dict:
        return self.context.data.get('hooks', {})

    def before_target(self):
        self._handle_log()
        self._handle_log_path()
        self._handle_workspace()
        self._handle_tf_vars()
        self._handle_hooks()

    def _handle_log(self):
        tf_log = self.config.get('log')
        if tf_log:
            self.context.push({'env': {'TF_LOG': tf_log}})

    def _handle_log_path(self):
        tf_log_path = self.config.get('log_path')
        if tf_log_path:
            self.context.push({'env': {'TF_LOG_PATH': tf_log_path}})

    def _handle_workspace(self):
        tf_workspace = self.config.get('workspace')
        if tf_workspace:
            self.context.push({'env': {'TF_WORKSPACE': tf_workspace}})

    def _handle_tf_vars(self):
        tf_vars = self.config.get('tf_vars', {})
        env = {f'TF_VAR_{key}': val for key, val in tf_vars.items()}
        if env:
            self.context.push({'env': env})

    def _handle_hooks(self):
        if self.context.data['args'][0] == 'terraform':
            self._handle_terraform_hook('before')
            self._handle_terraform_hook('after')
            self._handle_terraform_subcommand_hook('before')
            self._handle_terraform_subcommand_hook('after')

    def _handle_terraform_hook(self, before_or_after: str = 'before'):
        hook_name = f'{before_or_after}_terraform'
        if hook_name in self.hooks:
            hook = self.hooks[hook_name]
            if not isinstance(hook, list):
                hook = [hook]
            data = {'hooks': {f'{before_or_after}_target': hook}}
            self.context.push(data)

    def _handle_terraform_subcommand_hook(self, before_or_after: str = 'before'):
        subcommand = self.context.data['args'][1]
        hook_name = f'{before_or_after}_terraform_{subcommand}'
        if hook_name in self.hooks:
            hook = self.hooks[hook_name]
            if not isinstance(hook, list):
                hook = [hook]
            data = {'hooks': {f'{before_or_after}_target': hook}}
            self.context.push(data)
