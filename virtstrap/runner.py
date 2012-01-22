from optparse import OptionParser
from virtstrap.options import parser
from virtstrap.commands.init import Command as InitCommand
from virtstrap.commands.help import Command as HelpCommand

EXIT_FAIL = 1
EXIT_OK = 0

class VirtstrapRunner(object):
    """Routes commands to different commands"""
    def __init__(self):
        parser = OptionParser()
        self.parser = parser

    def main(self, args=None):
        """Runs the whole command line interface"""
        if not args:
            args = []
        parser = self.parser
        cli_options, cli_args = parser.parse_args(args=args)
        if not cli_args:
            parser.error('You must give a command (use "vstrap help" '
                    'to see a list of commands)')
        command = cli_args[0].lower()
        self.run_command(command)
        return EXIT_OK

    def run_command(self, name):
        """Load command from virtstrap.commands"""
        # FIXME fake information
        if name == 'init':
            command = InitCommand()
            command.run()
        elif name == 'help':
            command = HelpCommand()
            command.run()

def main(args=None):
    if args == ["--help"]:
        return 0
    return 1
