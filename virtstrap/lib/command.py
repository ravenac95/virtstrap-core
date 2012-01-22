class BaseCommand(object):
    name = None
    args = None
    description = None

    def __init__(self, parser=None):
        # Ensure that name, usage, and description
        # are defined
        assert self.name
        self.parser = parser

    def run(self, settings):
        raise NotImplementedError()
