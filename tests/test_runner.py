"""
Runner Tests
============

Very high level tests for the virtstrap runner. 
"""
import os
import sys
import fudge
from cStringIO import StringIO
from tests import fixture_path
from tests.tools import *
from nose.tools import raises
from nose.plugins.attrib import attr
from virtstrap import constants
from virtstrap.runner import VirtstrapRunner

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../'))
PACKAGES_DIR = os.path.abspath(os.path.join(PROJECT_DIR,
                    'tests/fixture/packages'))

TEST_CONFIG = """
requirements:
  - test1
  - test5

--- # Development profile
profile: development

requirements:
  - test4

---
profile: production

requirements:
  - test6
"""

def test_initialize_runner():
    """Test that we can initialize the VirtstrapRunner"""
    runner = VirtstrapRunner()

@fudge.test
def test_runner_lazy_load_registry():
    """Use a registry factory method to lazily load a registry"""
    fake_registry_factory = fudge.Fake()
    fake_registry_factory.expects_call().returns('reg')
    runner = VirtstrapRunner(registry_factory=fake_registry_factory)
    registry = runner.registry
    runner.set_registry('regtest')
    assert runner.registry == 'regtest'

@fudge.test
def test_runner_lazy_load_loader():
    """Use a loader factory method to lazily load a loader"""
    fake_loader_factory = fudge.Fake()
    fake_loader_factory.expects_call().returns('regtest')
    runner = VirtstrapRunner(loader_factory=fake_loader_factory)
    loader = runner.loader
    runner.set_loader('regtest')
    assert runner.loader == 'regtest'

class TestVirtstrapRunner(object):
    def setup(self):
        self.runner = VirtstrapRunner()

    def teardown(self):
        self.runner = None
    
    @fudge.test
    def test_runner_lists_commands(self):
        fake_registry = fudge.Fake()
        (fake_registry.expects('list_commands')
                .returns(['command1', 'command2']))
        self.runner.set_registry(fake_registry)
        commands = self.runner.list_commands()
        assert commands == ['command1', 'command2']

    @fudge.test
    def test_runner_run_command(self):
        """Test that the runner passes the correct data to the registry"""
        args = ('test', 'options')
        fake_registry = fudge.Fake()
        fake_registry.expects('run').with_args(*args)
        self.runner.set_registry(fake_registry)
        self.runner.run_command(*args)

    @fudge.patch('sys.stderr')
    def test_run_no_args(self, fake_stderr):
        """Run the main command line utility with no args"""
        fake_stderr.is_a_stub() # just want to silence stderr
        try:
            return_code = self.runner.main()
        except SystemExit, e:
            system_exit = True
            assert e.code == 2
        assert system_exit == True, "Runner didn't issue a system exit"

    def test_run_help(self):
        """Run help"""
        test_args = ['--help']
        system_exit = False
        try:
            code = self.runner.main(args=test_args)
        except SystemExit, e:
            system_exit = True
            assert e.code == 0
        assert system_exit == True, "Runner didn't issue a system exit"

    @attr('slow')
    def test_run_init(self):
        """Run the init command"""
        test_args = ['init']
        with in_temp_directory() as temp_dir:
            return_code = self.runner.main(args=test_args)
            virtual_environment_path = os.path.join(temp_dir, '.vs.env')
            quick_activate_path = os.path.join(temp_dir, 
                    constants.QUICK_ACTIVATE_FILENAME)
            assert os.path.exists(virtual_environment_path) == True
            assert os.path.exists(quick_activate_path) == True
            # Make sure quickactivate source's the activate script
            quick_activate = open(quick_activate_path)
            quick_activate_text = quick_activate.read()
            assert 'source' in quick_activate_text.strip()
            assert return_code == 0

    @attr('slow')
    def test_run_init_to_different_project_dir(self):
        """Run the init command in different project dir
        
        This test is pretty much identical to test_run_init
        it's performed in a project directory that isn't the CWD
        """
        # FIXME?
        # In order for this test to work. It cannot be in the 
        # Current development directory due to egg_info existing
        # for virtstrap within this directory. So for now we CD to
        # the fixture path
        with in_directory(fixture_path()):
            with temp_directory() as temp_dir:
                # Run the init to a project directory
                test_args = ['init', temp_dir] 
                
                return_code = self.runner.main(args=test_args)
    
                # Grab paths for testing
                virtual_environment_path = os.path.join(temp_dir, '.vs.env')
                quick_activate_path = os.path.join(temp_dir, 
                        constants.QUICK_ACTIVATE_FILENAME)
    
                # Make sure everything exists
                assert os.path.exists(virtual_environment_path) == True
                assert os.path.exists(quick_activate_path) == True
    
                # Make sure quickactivate source's the activate script
                quick_activate = open(quick_activate_path)
                quick_activate_text = quick_activate.read()
                assert 'source' in quick_activate_text.strip()
                assert return_code == 0

    @attr('slow')
    def test_run_init_env_different_directory(self):
        """Run the init command with a different virtstrap directory
        
        This tests that init can use a different virtstrap directory
        for its installation. However, when this happens you still need to
        link to the virtstrap directory locally. Otherwise you won't be able 
        to locate the project when running vstrap commands.
        """
        env_dir = 'envdir'
        test_args = ['init', '--virtstrap-dir=%s' % env_dir]
        with in_temp_directory() as temp_dir:
            return_code = self.runner.main(args=test_args)
            virtual_environment_path = os.path.join(temp_dir, env_dir)
            virtual_environment_path_link = os.path.join(temp_dir, '.vs.env')
            quick_activate_path = os.path.join(temp_dir, 
                    constants.QUICK_ACTIVATE_FILENAME)
            assert os.path.exists(virtual_environment_path) == True
            assert os.path.islink(virtual_environment_path_link) == True
            assert os.path.exists(quick_activate_path) == True
            assert return_code == 0
    
    @attr('slow')
    @hide_subprocess_stdout
    def test_run_init_with_a_config(self):
        """Run the init command with a VEfile in the directory

        Fairly self explanatory. It makes sure the VEfile's 
        requirements are installed
        """
        test_args = ['init']
        with temp_pip_index(PACKAGES_DIR) as index_url:
            with in_temp_directory() as temp_dir:
                # Create temp config file
                vefile = open(constants.VE_FILENAME, 'w')
                vefile.write(TEST_CONFIG)
                vefile.close()
                # If the config file was correctly written then 
                # it will install all the software
                return_code = self.runner.main(args=test_args)
                # Do a loose check of the requirements
                requirements = open('requirements.lock')
                requirements_string = requirements.read()
                expected_strings = ['test1==0.1', 'test5==1.4.3', 
                        'test4==0.4.1', 'test2==1.3', 'test3==0.10.1']
                for package in expected_strings:
                    assert package in requirements_string
                assert return_code == 0

    @attr('slow')
    @hide_subprocess_stdout
    def test_run_init_with_a_config_using_custom_config_file(self):
        """Run the init command with a custom config file in the directory

        Uses a file other than VEfile for the configuration.
        """
        custom_config_file = 'testfile'
        test_args = ['init', '--config-file=%s' % custom_config_file]
        with temp_pip_index(PACKAGES_DIR) as index_url:
            with in_temp_directory() as temp_dir:
                # Create the custom config file
                vefile = open(custom_config_file, 'w')
                vefile.write(TEST_CONFIG)
                vefile.close()
                return_code = self.runner.main(args=test_args)
                # Do a loose check of the requirements
                requirements = open('requirements.lock')
                requirements_string = requirements.read()
                expected_strings = ['test1', 'test5', 'test4']
                for package in expected_strings:
                    assert package in requirements_string
                assert return_code == 0

    @attr('slow')
    @hide_subprocess_stdout
    def test_run_init_using_different_profile(self):
        """Run the init command using a different profile"""
        profiles = 'production'
        test_args = ['init', '--profiles=%s' % profiles]
        with temp_pip_index(PACKAGES_DIR) as index_url:
            with in_temp_directory() as temp_dir:
                vefile = open(constants.VE_FILENAME, 'w')
                vefile.write(TEST_CONFIG)
                vefile.close()
                return_code = self.runner.main(args=test_args)
                # Do a loose check of the requirements
                requirements = open('requirements.lock')
                requirements_string = requirements.read()
                expected_strings = ['test1', 'test5', 'test6']
                for package in expected_strings:
                    assert package in requirements_string
                assert return_code == 0
