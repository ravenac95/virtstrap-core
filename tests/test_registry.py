import fudge
from virtstrap.registry import CommandRegistry

def test_initialize_registry():
    registry = CommandRegistry()

class TestCommandRegistry(object):
    def setup(self):
        self.registry = CommandRegistry()

    def test_register_a_command(self):
        """Test that a command registers correctly"""
        class FakeCommand(object):
            name = 'test'
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.retrieve('test') == FakeCommand

    @fudge.test
    def test_run_a_command(self):
        """Test that a command runs correctly"""
        from virtstrap.commands import Command
        # Setup fake command instance
        command_args = ('test', 'options')
        class FakeCommand(Command):
            name = 'test'
            called = False
            def run(self, options):
                self.__class__.called = True
                assert options == 'options'

        #register to the registry
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.run(*command_args) == 0
        assert FakeCommand.called

    @fudge.test
    def test_run_a_command_with_fake_kwargs(self):
        """Test that a command runs correctly with fake kwargs"""
        from virtstrap.commands import Command
        # Setup fake command instance
        command_args = ('test', 'options')
        class FakeCommand(Command):
            name = 'test'
            called = False
            def run(self, options):
                self.__class__.called = True
                assert options == 'options'

        #register to the registry
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.run(*command_args, test='test') == 0
        assert FakeCommand.called


