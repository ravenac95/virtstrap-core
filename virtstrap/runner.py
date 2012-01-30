import sys
from optparse import OptionParser
from virtstrap.log import logger, setup_logger
from virtstrap.loaders import CommandLoader
from virtstrap.commands import registry
from virtstrap.registry import CommandDoesNotExist
from virtstrap.config import VirtstrapConfig

EXIT_FAIL = 1
EXIT_OK = 0

class VirtstrapRunner(object):
    """Routes commands to different commands"""
    def main(self, args=None):
        """Handles execution through command line interface"""
        # Load all of the available commands
        self.load_commands()
        parser = self.create_parser()
        if not args:
            args = sys.argv[1:]
        cli_args = parser.parse_args(args=args)
        config = self.handle_global_options(cli_args)
        command = cli_args.command
        # Run the command
        try:
            exit_code = self.run_command(command, config, cli_args)
        except CommandDoesNotExist:
            exit_code = EXIT_FAIL
            logger.debug('Unknown command "%s"' % command)
            parser.error('"%s" is not a vstrap command. (use "vstrap help" '
                    'to see a list of commands)' % command)
        return exit_code

    def handle_global_options(self, cli_args):
        setup_logger(cli_args.verbosity, 
                cli_args.no_colored_output)
        return self.load_configuration(cli_args)

    def load_configuration(self, cli_args):
        try:
            config_file_obj = open(cli_args.config_file)
        except IOError:
            config_file_obj = ''
        config = VirtstrapConfig.from_string(config_file_obj, 
                profiles=cli_args.profiles)
        return config

    def load_commands(self):
        """Tell loader to load commands"""
        command_loader = CommandLoader()
        command_loader.load()

    def create_parser(self):
        return registry.create_cli_parser()

    def run_command(self, name, config, cli_args):
        """Load command from virtstrap.commands"""
        logger.debug('Command "%s" chosen' % name)
        options = cli_args.__dict__
        return registry.run(name, config, **options)


def main(args=None):
    runner = VirtstrapRunner()
    exit = runner.main(args=args)
    if exit:
        sys.exit(exit)
