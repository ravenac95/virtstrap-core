"""
Test Base Command
=================
"""
import fudge
from nose.tools import *
from tests import fixture_path
from tests.tools import *
from virtstrap.basecommand import Command, ProjectMixin, ProjectCommand

class FakeCommand(Command):
    name = 'fake'
    args = ['argument_one']
    description = 'Fake Description'

    def __init__(self, test_obj):
        super(FakeCommand, self).__init__()
        self.test_obj = test_obj

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

def test_run_with_exception():
    """Test when a command's run method raises an exception.
    
    The run command is wrapped in the execute method
    """
    class FakeCommand(Command):
        name = 'test'
        def run(self, *args, **kwargs):
            raise Exception('Forced Error')
    command = FakeCommand()
    assert command.execute('config', 'option') == 2

@fudge.patch('virtstrap.basecommand.Project')
def test_project_mixin_loads_project(FakeProject):
    """Test ProjectMixin"""
    class FakeCommand(Command, ProjectMixin):
        name = "test"
    FakeProject.expects('load').with_args('config', 'options').returns('proj')
    fake = FakeCommand()
    project = fake.load_project('config', 'options')
    assert project == 'proj'

@fudge.patch('virtstrap.basecommand.Project')
def test_project_mixin_loads_project(FakeProject):
    """Test ProjectMixin"""
    class FakeCommand(Command, ProjectMixin):
        name = 'test'
    FakeProject.expects('load').with_args('config', 'options').returns('proj')
    fake = FakeCommand()
    project = fake.load_project('config', 'options')
    assert project == 'proj'

@fudge.patch('virtstrap.basecommand.Project')
def test_project_command_runs_with_project(FakeProject):
    """Test ProjectCommand runs correctly"""
    class FakeProjectCommand(ProjectCommand):
        name = 'test'
        def run(self, project, options):
            assert project == 'proj'
    (FakeProject.expects('load')
            .with_args('config', 'options').returns('proj'))
    command = FakeProjectCommand()
    return_code = command.execute('config', 'options')
    assert return_code == 0

def test_project_command_runs_with_project_not_faked():
    """Test ProjectCommand in a sandbox"""
    class FakeProjectCommand(ProjectCommand):
        name = 'test'
        def run(self, project, options):
            assert project.name == 'sample_project'
            assert project.env_path().endswith('sample_project/.vs.env')
    from virtstrap.config import VirtstrapConfig
    from virtstrap.options import create_base_parser
    base_parser = create_base_parser()
    base_options = base_parser.parse_args(args=[])
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    with in_directory(fake_project_sub_directory):
        config = VirtstrapConfig.from_string('')
        command = FakeProjectCommand()
        return_code = command.execute(config, base_options)
        assert return_code == 0
