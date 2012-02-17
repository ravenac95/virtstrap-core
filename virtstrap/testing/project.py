"""
virtstrap.testing.project
-------------------------

Test tools for projects
"""
from contextlib import contextmanager
import virtualenv
import fudge
from virtstrap.testing import *
from virtstrap import constants
from virtstrap.project import Project
from virtstrap.options import create_base_parser

class FakeProject(Project):
    def patch_method(self, method_name):
        fake_method = fudge.Fake()
        fake_method.expects_call()
        setattr(self, method_name, fake_method)
        return fake_method

@contextmanager
def temp_project():
    """Creates a temporary project directory within a temporary directory
    
    This is useful for testing ProjectCommands.
    """
    base_parser = create_base_parser()
    options = base_parser.parse_args(args=[])
    with in_temp_directory() as temp_dir:
        os.mkdir(constants.VIRTSTRAP_DIR)
        virtualenv.create_environment(constants.VIRTSTRAP_DIR, 
                site_packages=False)
        options.project_dir = temp_dir
        project = FakeProject.load(options)
        yield project, options, temp_dir

