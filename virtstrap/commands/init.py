import os
import virtualenv
import sys
import tempfile
from argparse import ArgumentParser
from virtstrap.lib.caller import call
from virtstrap import commands
from virtstrap import constants
from virtstrap.lib.command import Command
from virtstrap.requirements import RequirementSet

parser = ArgumentParser()
parser.add_argument('PROJECT_DIR',
        help="project's root directory",
        nargs='?', default='.')

def process_requirements_config(raw_requirements):
    requirement_set = RequirementSet.from_config_data(raw_requirements)
    return requirement_set

class InstallationError(Exception):
    pass

class InitializeCommand(Command):
    name = 'init'
    parser = parser
    description = 'Bootstraps a virtstrap virtual environment'

    def run(self, config, **options):
        self.create_virtualenv(config, options)
        self.create_quickactivate_script(config, options)
        self.build_requirements(config, options)

    def create_virtualenv(self, config, options):
        """Create virtual environment in the virtstrap directory"""
        virtstrap_dir_relpath = options.get('virtstrap_dir')
        virtstrap_dir = os.path.abspath(virtstrap_dir_relpath)
        self.logger.info('Creating virtualenv in %s' % virtstrap_dir)
        virtualenv.create_environment(virtstrap_dir,
                site_packages=False,
                prompt="(%s) " % 'proj')

    def build_requirements(self, config, options):
        """Build the requirements specified in config"""
        logger = self.logger
        logger.info('Building requirements in "%s"' % 
                options.get('config_file'))
        # Process the requirements into a requirement set
        requirement_set = config.process_section('requirements', 
                process_requirements_config)
        requirements_string = requirement_set.to_pip_str()
        if requirements_string:
            # Write the requirements to a temporary file
            os_handle, temp_reqs_path = tempfile.mkstemp()
            temp_reqs_file = open(temp_reqs_path, 'w')
            temp_reqs_file.write(requirements_string)
            temp_reqs_file.close()
            
            # Get new path data
            virtstrap_dir = os.path.abspath(options.get('virtstrap_dir'))
            virtstrap_bin_path = os.path.join(virtstrap_dir, 'bin')
            # Temporarily change the path to the new one
            old_path = os.environ['PATH']
            os.environ['PATH'] = '%s:%s' % (virtstrap_bin_path, old_path)
            try:
                self.run_pip_install(virtstrap_bin_path, temp_reqs_path)
            except InstallationError:
                # Exit if any problems occur during installation
                self.logger.error('Installation could not be completed. '
                        'Aborting')
                sys.exit(2)
            finally:
                logger.debug('Removing temporary requirements file')
                os.remove(temp_reqs_path)
            os.environ['PATH'] = old_path
        requirements_file = open('requirements.txt', 'w')
        requirements_file.write(requirements_string)
        requirements_file.close()

    def run_pip_install(self, virtstrap_bin_path, requirements_file):
        # Run pip to install packages
        pip_bin = os.path.join(virtstrap_bin_path, 'pip')
        pip_command = 'install'
        self.logger.info('Running pip at %s' % pip_bin)
        return_code = call([pip_bin, pip_command, "-r", 
                requirements_file])
        if return_code != 0:
            raise InstallationError('An error occured during installation')

    def create_quickactivate_script(self, config, options):
        """Create a quickactivate script"""
        self.logger.info('Creating quick activate script')
        quick_activate = open('./quickactivate.sh', 'w')
        quick_activate.write("source")
        quick_activate.close()

commands.register(InitializeCommand)
