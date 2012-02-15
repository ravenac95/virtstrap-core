"""
virtstrap.loaders
-----------------

Loads commands from various locations. Currently only loads 
virtstrap.commands.*
"""

import os
import inspect
from virtstrap.log import logger
from virtstrap.utils import import_string

class CommandLoader(object):
    def __init__(self, builtins=None):
        self._builtins = builtins or 'virtstrap.commands'

    def load(self):
        """Collects all commands"""
        self._load_builtin_commands()

    def _load_builtin_commands(self):
        commands = import_string(self._builtins)
        builtin_command_dir = os.path.abspath(os.path.dirname(commands.__file__))

        import_template = '%s.%s' % (commands.__name__, '%s')

        builtin_command_files = os.listdir(builtin_command_dir)

        for filename in builtin_command_files:
            if filename.endswith('.py') and not filename == '__init__.py':
                # Load the file. That's all that should be necessary
                module_name = filename[:-3]
                import_path_string = import_template % module_name
                try:
                    command_module = import_string(import_path_string)
                except ImportError:
                    logger.exception('Failed to load builtin command '
                        'module "%s"' % filename)
                else:
                    self._load_commands_in_module(command_module)

    def _load_commands_in_module(self, module):
        """Loads all subclasses of Command in a particular module"""
        print module
        from virtstrap import commands
        for name, variable in module.__dict__.iteritems():
            if inspect.isclass(variable):
                bases = inspect.getmro(variable)
                if commands.Command in bases:
                    commands.registry.register(variable)
