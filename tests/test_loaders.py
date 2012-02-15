from virtstrap import commands
from virtstrap.loaders import *

def registry_command_names_set():
    command_names = set()
    print id(commands.registry)
    for command_name, command in commands.registry.commands_iter():
        command_names.add(command_name)
    return command_names

class TestLoader(object):
    def setup(self):
        commands.registry = commands.CommandRegistry()

    def teardown(self):
        commands.registry = None

    def test_load(self):
        loader = CommandLoader(builtins='virtstrap.commands')
        loader.load()
        expected = set(['init', 'clean', 'install', 'info'])
        command_names = registry_command_names_set()
        assert command_names == expected
    
    def test_load_nothing(self):
        loader = CommandLoader(builtins='tests.nocommands')
        loader.load()
        expected = set()
        command_names = registry_command_names_set()
        assert command_names == expected
