"""
virtstrap.commands.init
-----------------------

The 'init' command
"""
import os
import sys
import shutil
from argparse import ArgumentParser
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
        virtstrap_env = os.environ.get('VIRTSTRAP_ENV')
        virtstrap_dev_env = os.environ.get('VIRTSTRAP_DEV_ENV')
        # the init command cannot be run in virtstrap environment
        if virtstrap_env and not virtstrap_dev_env:
            self.logger.error('init command cannot be run from inside a ' 
                'virtstrap environment unless the environment variable '
                '"VIRTSTRAP_DEV_ENV" is set.')
            sys.exit(2)
        import virtualenv
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
        self.install_virtstrap(project)

    def install_virtstrap(self, project):
        try:
            import virtstrap_support
        except ImportError:
            self.logger.error('Virtstrap is improperly installed or '
                    'being called from inside another virtstrap. Please '
                    'check your installation.')
            sys.exit(2)
        # Set the directory to the correct files
        pip_bin = 'pip'
        pip_command = 'install'
        pip_find_links = ('--find-links=file://%s' % 
                virtstrap_support.file_directory())
        pip_args = [pip_command, pip_find_links, '--no-index', 
                'virtstrap']
        # TODO REMOVE dev once we're ready
        # Add a test for this 
        self.logger.debug('Installing virtstrap into environment')
        extra_env = dict(VIRTSTRAP_ENV=project.env_path())
        remove_from_env = ['VIRTSTRAP_DEV_ENV']
        try:
            project.call_bin(pip_bin, pip_args, extra_env=extra_env,
                    remove_from_env=remove_from_env, show_stdout=False)
        except OSError:
            self.logger.error('An error occured with pip')
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
