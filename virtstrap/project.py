"""
virtstrap.project
-----------------
"""
import os
from virtstrap import constants

VIRTSTRAP_DIR = constants.VIRTSTRAP_DIR

class Project(object):
    @classmethod
    def load(cls, config, options):
        """Creates a project and loads it's configuration immediately"""
        project = cls()
        project.load_settings(config, options)
        return project

    def __init__(self):
        self._options = None
        self._config = None
    
    def load_settings(self, config, options):
        self._options = options
        self._config = config
        # Check if project directory is specified
        project_dir = getattr(options, 'project_dir', None)
        if not project_dir:
            project_dir = self._find_project_dir()
        self._project_dir = project_dir
        processor = ProjectNameProcessor(project_dir)
        project_name = config.process_section('project_name', processor)
        self._project_name = project_name

    def _find_project_dir(self):
        return find_project_dir()

    @property
    def name(self):
        return self._project_name

    def set_options(self, options):
        self._options = options

    def path(self, *paths):
        """Create a path relative to the project"""
        return os.path.join(self._project_dir, *paths)

    def env_path(self, *paths):
        """Create a path relative to the virtstrap-dir"""
        return os.path.join(self._options.virtstrap_dir, *paths)

    def bin_path(self, *paths):
        """Create a path relative to the virtstrap-dir's bin directory"""
        return self.env_path('bin', *paths)

def find_project_dir(current_dir=None):
    """Finds the project directory for the current directory"""
    current_dir = current_dir or os.path.abspath(os.curdir)
    if VIRTSTRAP_DIR in os.listdir(current_dir):
        vs_dir = os.path.join(current_dir, VIRTSTRAP_DIR)
        if os.path.islink(vs_dir) or os.path.isdir(vs_dir):
            return current_dir
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    return find_project_dir(parent_dir)

class ProjectNameProcessor(object):
    def __init__(self, project_dir):
        self._project_dir = os.path.abspath(project_dir)

    def __call__(self, project_name):
        return project_name or os.path.basename(self._project_dir)

