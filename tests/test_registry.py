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
        # Setup fake command instance
        fake_instance = fudge.Fake()
        (fake_instance.expects('execute')
                .with_args('config', 'options')
                .returns('retval'))
        # Setup fake command class
        FakeCommand = fudge.Fake()
        FakeCommand.has_attr(name='test')
        FakeCommand.expects_call().returns(fake_instance)

        #register to the registry
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.run('test', 'config', 'options') == 'retval'
