"""
Runner Tests
============

Very high level tests for the virtstrap runner
"""
import os
import fudge
from cStringIO import StringIO
from virtstrap.runner import VirtstrapRunner
from tests.tools import *
from nose.tools import raises

def test_initialize_runner():
    """Test that we can initialize the VirtstrapRunner"""
    runner = VirtstrapRunner()

class TestVirtstrapRunner(object):
    def setup(self):
        self.runner = VirtstrapRunner()

    def teardown(self):
        self.runner = None

    @fudge.patch('sys.stderr')
    def test_run_no_args(self, fake_sys_stderr):
        """Run the main command line utility with no args"""
        fake_sys_stderr.is_a_stub() # just want to silence stderr
        try:
            return_code = self.runner.main()
        except SystemExit, e:
            system_exit = True
            assert e.code == 2
        assert system_exit == True, "Runner didn't issue a system exit"

    def test_run_help(self):
        """Run the help command"""
        test_args = ['--help']
        system_exit = False
        try:
            code = self.runner.main(args=test_args)
        except SystemExit, e:
            system_exit = True
            assert e.code == 0
        assert system_exit == True, "Runner didn't issue a system exit"

    def test_run_init(self):
        """Run the init command"""
        test_args = ['init']
        with in_temp_directory() as temp_directory:
            return_code = self.runner.main(args=test_args)
            virtual_environment_path = os.path.join(temp_directory, ".vs.env")
            quick_activate_path = os.path.join(temp_directory, "quickactivate.sh")
            assert os.path.exists(virtual_environment_path) == True
            assert os.path.exists(quick_activate_path) == True
            assert return_code == 0

    def test_run_init_builds_to_different_directory(self):
        env_dir = 'envdir'
        test_args = ['init', '--virtstrap-dir=%s' % env_dir]
        with in_temp_directory() as temp_directory:
            return_code = self.runner.main(args=test_args)
            virtual_environment_path = os.path.join(temp_directory, env_dir)
            quick_activate_path = os.path.join(temp_directory, "quickactivate.sh")
            assert os.path.exists(virtual_environment_path) == True
            assert os.path.exists(quick_activate_path) == True
            assert return_code == 0

