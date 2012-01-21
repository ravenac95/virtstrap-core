"""
Test Base Command
=================
"""
import fudge
from nose.tools import *
from virtstrap.lib.command import Command

class FakeCommand(Command):
    name = 'fake'
    usage = '%prog'
    description = 'Fake Description'

    def __init__(self, test_obj):
        super(FakeCommand, self).__init__()
        self.test_stream = test_stream
        parser = self.parser
        parser.add_option("-t", "--test", dest="test")

    def run(self, *args, **kwargs):
        self.test_obj.write("This is a test")

@fudge.test
def test_initialize_command():
    """Test initializing fake command."""
    command = FakeCommand(None)

@raises(AssertionError)
def test_initialize_base_command():
    """Test initializing the base command. Should fail"""
    command = Command()
