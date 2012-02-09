"""
virtstrap.loaders
-----------------

Loads commands from various locations. Currently only loads 
virtstrap.commands.*
"""

import os
from virtstrap.log import logger

class CommandLoader(object):
    def load(self):
        """Collects all commands"""
        self._load_builtin_commands()

    def _load_builtin_commands(self):
        from virtstrap import commands
        builtin_command_dir = os.path.abspath(os.path.dirname(commands.__file__))

        import_template = '%s.%s' % (commands.__name__, '%s')

        builtin_command_files = os.listdir(builtin_command_dir)

        for filename in builtin_command_files:
            if filename.endswith('.py'):
                # Load the file. That's all that should be necessary
                module_name = filename[:-3]
                import_string = import_template % module_name
                try:
                    __import__(import_string)
                except ImportError:
                    logger.exception('Failed to load builtin command '
                        'module "%s"' % filename)

