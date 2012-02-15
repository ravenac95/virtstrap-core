"""
virtstrap.runner
----------------

The main runner for the virtstrap application. If you wish to call
virtstrap from within your program. The simplest way would be to use
the runner and feed it the arguments.
"""

import sys
import os
from optparse import OptionParser
from virtstrap import constants
from virtstrap import commands
from virtstrap.log import logger, setup_logger
from virtstrap.loaders import CommandLoader
from virtstrap.registry import CommandDoesNotExist, CommandRegistry

EXIT_FAIL = 1
EXIT_OK = 0

class VirtstrapRunner(object):
    """Routes command line to different commands"""
    def __init__(self, registry=None):
        self.registry = registry

    def set_registry(self, registry):
        self.registry = registry

    def main(self, args=None):
        """Handles execution through command line interface"""
        # Load all of the available commands
        self.load_commands()
        parser = self.create_parser()
        if not args:
            args = sys.argv[1:]
        cli_args = parser.parse_args(args=args)
        self.handle_global_options(cli_args)
        command = cli_args.command
        # Run the command
        try:
            exit_code = self.run_command(command, cli_args)
        except CommandDoesNotExist:
            exit_code = EXIT_FAIL
            logger.debug('Unknown command "%s"' % command)
            parser.error('"%s" is not a vstrap command. (use "vstrap help" '
                    'to see a list of commands)' % command)
        finally:
            self.close_context()
        if exit_code == EXIT_OK:
            # TODO actually delete the correct log file
            if os.path.exists(constants.LOG_FILE): 
                os.remove(constants.LOG_FILE)
        return exit_code

    def handle_global_options(self, cli_args):
        setup_logger(cli_args.verbosity, 
                cli_args.no_colored_output)

    def load_commands(self):
        """Tell loader to load commands"""
        registry = CommandRegistry()
        self.registry = registry
        commands.registry = registry
        command_loader = CommandLoader()
        command_loader.load()

    def close_context(self):
        """Removes the registry from the commands"""
        self.registry = None
        commands.registry = None

    def create_parser(self):
        return self.registry.create_cli_parser()

    def run_command(self, name, cli_args):
        """Load command from virtstrap.commands"""
        logger.debug('Command "%s" chosen' % name)
        options = cli_args
        return self.registry.run(name, options)


def main(args=None):
    runner = VirtstrapRunner()
    exit = runner.main(args=args)
    if exit:
        sys.exit(exit)
