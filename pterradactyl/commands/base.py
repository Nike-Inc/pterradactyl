class AbstractBaseCommand(object):

    def __init__(self, config, parser):
        self.config = config

    def argument(self, *args, **kwargs):
        pass

    def command_name(self):
        pass

    def execute(self, args, terraform_args):
        pass
