from virtstrap.log import logger
from argparse import ArgumentParser

class Command(object):
    name = None
    args = None
    parser = ArgumentParser()
    description = None
    options = None

    def __init__(self):
        # Ensure that name, usage, and description
        # are defined
        assert self.name
        self.options = []
        self.logger = logger

    def execute(self, config, **options):
        try:
            self.run(config, **options)
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return 2
        return 0

    def handle_parser(self, parser):
        """Special override to do low-level parser handling"""
        pass

    def run(self, *args, **options):
        raise NotImplementedError('This command does nothing')
