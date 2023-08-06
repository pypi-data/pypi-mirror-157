# internal
from laz.plugins.plugin import Plugin


class AwsPlugin(Plugin):

    def before_target(self):
        env = {}
        aws_profile = self.context.data.get('aws', {}).get('profile')
        if aws_profile is not None:
            env['AWS_PROFILE'] = aws_profile
        aws_region = self.context.data.get('aws', {}).get('region')
        if aws_region is not None:
            env['AWS_DEFAULT_REGION'] = aws_region
        if env:
            self.context.push({'env': env})
