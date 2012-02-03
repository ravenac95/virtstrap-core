import os
from virtstrap import constants

VIRTSTRAP_DIR = constants.VIRTSTRAP_DIR

class Project(object):
    def __init__(self):
        self._options = None

    def load_options(self, options):
        self._options = options
        # Check if project directory is specified
        project_dir = getattr(options, 'project_dir', None)
        if not project_dir:
            project_dir = self._find_project_dir()
        self.project_dir = project_dir

    def _find_project_dir(self):
        return find_project_dir()

    def set_options(self, options):
        self._options = options

    def make_project_path(self, *paths):
        """Create a path relative to the project"""
        return os.path.join(self.project_dir, *paths)

    def make_env_path(self, *paths):
        """Create a path relative to the virtstrap-dir"""
        return os.path.join(self._options.virtstrap_dir, *paths)

    def make_bin_path(self, name):
        """Create a path relative to the virtstrap-dir's bin directory"""
        return self.make_env_path('bin', name)

def find_project_dir(current_dir=None):
    """Finds the project directory for the current directory"""
    current_dir = current_dir or os.path.abspath(os.curdir)
    if VIRTSTRAP_DIR in os.listdir(current_dir):
        vs_dir = os.path.join(current_dir, VIRTSTRAP_DIR)
        if os.path.islink(vs_dir) or os.path.isdir(vs_dir):
            return current_dir
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    return find_project_dir(parent_dir)
