"""
Test Base Command
=================
"""
import fudge
from nose.tools import *
from virtstrap.lib.command import BaseCommand

class FakeCommand(BaseCommand):
    name = 'fake'
    args = ['argument_one']
    description = 'Fake Description'

    def __init__(self, test_obj, **kwargs):
        super(FakeCommand, self).__init__(**kwargs)
        self.test_obj = test_obj
        parser = self.parser
        parser.add_option("-t", "--test", dest="test")

    def run(self, *args, **kwargs):
        self.test_obj.write("This is a test")

@fudge.test
def test_initialize_command():
    """Test initializing fake command."""
    fake_parser = fudge.Fake('parser').expects('add_option')
    command = FakeCommand(None, parser=fake_parser)

@raises(AssertionError)
def test_initialize_base_command():
    """Test initializing the base command. Should fail"""
    command = BaseCommand()
