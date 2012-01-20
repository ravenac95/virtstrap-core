from virtstrap import runner
from tests.tools import *

def test_run_no_args():
    """Run the main command line utility with no args"""
    return_code = runner.main()
    # No args means it should return an error value
    assert return_code == 1

def test_run_help():
    test_args = ['--help']
    return_code = runner.main(args=test_args)
    assert return_code == 0

def test_run_init():
    test_args = ['init', '.']
