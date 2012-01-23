from virtstrap.log import logger
from virtstrap.options import create_parser

class Command(object):
    name = None
    args = None
    description = None
    options = None

    def __init__(self):
        # Ensure that name, usage, and description
        # are defined
        assert self.name
        self.options = []
        self.logger = logger

    def execute(self, command_args, base_options):
        parser = create_parser(self.name, self.args)
        parser.add_options(self.options)
        self.handle_parser(parser)

        cli_options, cli_args = parser.parse_args(command_args)
        
        try:
            self.run(*cli_args, **cli_options.__dict__)
        except:
            self.logger.exception("dude")
            #self.logger.exception('An error occured executing command "%s"' %
                    #self.__class__.__name__)
            return 2
        return 0

    def handle_parser(self, parser):
        """Special override to do low-level parser handling"""
        pass

    def run(self, *args, **options):
        raise NotImplementedError('This command does nothing')
