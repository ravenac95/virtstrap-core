"""
virtstrap.commands.init
-----------------------

The 'init' command
"""
import os
import subprocess
import shutil
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
        self.wrap_activate_script(project)
        self.create_quick_activate_script(project)
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

        # Install virtstrap into virtualenv
        # FIXME add later. with optimizations. This is really slow
        # self.install_virtstrap(project)

    def install_virtstrap(self, project):
        pip_bin = project.bin_path('pip')
        pip_command = 'install'
        # TODO REMOVE dev once we're ready
        # Add a test for this 
        self.logger.debug('Installing virtstrap into environment')
        process = subprocess.Popen([pip_bin, pip_command, 
            'virtstrap==dev'], stdout=subprocess.PIPE)
        return_code = process.wait()
        if return_code != 0:
            self.logger.error('Error installing virtstrap')
            sys.exit(2)
        

    def wrap_activate_script(self, project):
        """Creates a wrapper around the original activate script"""
        self.logger.info('Wrapping original activate script')
        # Copy old activate script
        activate_path = project.bin_path('activate') # The normal path
        old_activate_path = project.bin_path('ve_activate') # Dest path
        shutil.copy(activate_path, old_activate_path)

        # Using a template, create the new one
        new_activate_script = self.render_template('init/activate.sh.jinja')
        activate_file = open(activate_path, 'w')
        activate_file.write(new_activate_script)

    def create_quick_activate_script(self, project):
        """Create a quickactivate script

        This script is purely for convenience. Eventually it will be made
        optional and something more convenient will be provided. However,
        at this time. This makes it much easier than typing in

            $ source .vs.env/bin/activate
        """
        self.logger.info('Creating quick activate script')
        quick_activate_path = project.path(constants.QUICK_ACTIVATE_FILENAME)
        quick_activate_script = self.render_template(
                'init/quickactivate.sh.jinja')
        quick_activate = open(quick_activate_path, 'w')
        quick_activate.write(quick_activate_script)
        quick_activate.close()

commands.register(InitializeCommand)
