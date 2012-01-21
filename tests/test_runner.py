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
        fake_sys_stderr.is_a_stub()
        try:
            return_code = self.runner.main()
        except SystemExit, e:
            system_exit = True
            assert e.code == 2
        assert system_exit == True, "Runner didn't issue a system exit"

    def test_run_help(self):
        test_args = ['--help']
        system_exit = False
        try:
            self.runner.main(args=test_args)
        except SystemExit, e:
            system_exit = True
            assert e.code == 0
        assert system_exit == True, "Runner didn't issue a system exit"

    def test_run_init(self):
        test_args = ['init', '.']
        with in_temp_directory() as temp_directory:
            return_code = self.runner.main(args=test_args)
            virtual_environment_path = os.path.join(temp_directory, ".vs.env")
            assert os.path.exists(virtual_environment_path) == True
            assert return_code == 0
