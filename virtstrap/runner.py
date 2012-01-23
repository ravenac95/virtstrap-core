import sys
from optparse import OptionParser
from virtstrap.log import logger, setup_logger
from virtstrap.options import create_parser
from virtstrap.loaders import CommandLoader
from virtstrap.commands import registry
from virtstrap.registry import CommandDoesNotExist

EXIT_FAIL = 1
EXIT_OK = 0

class VirtstrapRunner(object):
    """Routes commands to different commands"""
    def main(self, args=None):
        """Handles execution through command line interface"""
        if not args:
            args = sys.argv[1:]
        parser = create_parser()
        cli_options, cli_args = parser.parse_args(args=args)
        self.handle_global_options(cli_options)
        if not cli_args:
            if cli_options.help:
                cli_args = ['help']
            else:
                parser.error('You must give a command (use "vstrap help" '
                    'to see a list of commands)')
        command = cli_args[0].lower()
        # Load Commands
        self.load_commands()
        # Run the command
        try:
            exit_code = self.run_command(command, cli_args[1:], cli_options)
        except CommandDoesNotExist:
            exit_code = EXIT_FAIL
            logger.debug('Unknown command "%s"' % command)
            parser.error('"%s" is not a vstrap command. (use "vstrap help" '
                    'to see a list of commands)' % command)
        return exit_code

    def handle_global_options(self, global_options):
        setup_logger(global_options.verbosity, 
                global_options.no_colored_output)

    def load_commands(self):
        """Tell loader to load commands"""
        command_loader = CommandLoader()
        command_loader.load()

    def run_command(self, name, args, base_options,):
        """Load command from virtstrap.commands"""
        # FIXME fake information
        logger.debug('Command "%s" chosen' % name)
        return registry.run(name, args, base_options)


def main(args=None):
    runner = VirtstrapRunner()
    exit = runner.main(args=args)
    if exit:
        sys.exit(exit)
