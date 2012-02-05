import os
from argparse import ArgumentParser
import virtualenv
from virtstrap import commands
from virtstrap import constants

parser = ArgumentParser()
parser.add_argument('project_dir', metavar='PROJECT_DIR',
        help="project's root directory",
        nargs='?', default='.')

class InitializeCommand(commands.ProjectCommand):
    name = 'init'
    parser = parser
    description = 'Bootstraps a virtstrap virtual environment'

    def run(self, project, options):
        self.create_virtualenv(project)
        self.create_quickactivate_script(project)
        commands.run('install', options, project=project)

    def create_virtualenv(self, project):
        """Create virtual environment in the virtstrap directory"""
        virtstrap_dir = project.env_path()
        project_name = project.name
        self.logger.info('Creating virtualenv in %s for "%s"' % (
            virtstrap_dir, project_name))
        # Create the virtualenv
        virtualenv.create_environment(virtstrap_dir,
                site_packages=False,
                prompt="(%s) " % project_name)
        expected_virtstrap_dir = project.path(constants.VIRTSTRAP_DIR)
        if virtstrap_dir != expected_virtstrap_dir:
            # if the expected project path isn't there then make sure
            # we have a link at the expected location.
            os.symlink(virtstrap_dir, expected_virtstrap_dir)

    def create_quickactivate_script(self, project):
        """Create a quickactivate script"""
        self.logger.info('Creating quick activate script')
        quick_activate_path = project.path('quickactivate.sh')
        quick_activate = open(quick_activate_path, 'w')
        quick_activate.write("source")
        quick_activate.close()

commands.register(InitializeCommand)
