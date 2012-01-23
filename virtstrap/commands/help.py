from virtstrap import commands
from virtstrap.lib.command import Command

class HelpCommand(Command):
    name = 'help'
    description = 'Displays this help text'

    def handle_parser(self, parser):
        parser.print_help()
        # Display commands
        commands.registry.print_command_help()

    def run(self, *args, **kwargs):
        pass

commands.register(HelpCommand)
