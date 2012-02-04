import os
import sys
import tempfile
from argparse import ArgumentParser
from subprocess import call
import virtualenv
from virtstrap import commands
from virtstrap import constants
from virtstrap.requirements import RequirementSet

parser = ArgumentParser()
parser.add_argument('project_dir', metavar='PROJECT_DIR',
        help="project's root directory",
        nargs='?', default='.')

def process_requirements_config(raw_requirements):
    requirement_set = RequirementSet.from_config_data(raw_requirements)
    return requirement_set

class InstallationError(Exception):
    pass

class InitializeCommand(commands.ProjectCommand):
    name = 'init'
    parser = parser
    description = 'Bootstraps a virtstrap virtual environment.'

    def run(self, project, options):
        self.create_virtualenv(project)
        self.create_quickactivate_script(project)
        #raise Exception()
        self.build_requirements(project, options)

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

    def build_requirements(self, project, options):
        """Build the requirements specified in config"""
        logger = self.logger
        logger.info('Building requirements in "%s"' % options.config_file)
        # Process the requirements into a requirement set
        requirement_set = project._config.process_section('requirements', 
                process_requirements_config)
        requirements_string = requirement_set.to_pip_str()
        if requirements_string:
            # Write the requirements to a temporary file
            os_handle, temp_reqs_path = tempfile.mkstemp()
            temp_reqs_file = open(temp_reqs_path, 'w')
            temp_reqs_file.write(requirements_string)
            temp_reqs_file.close()
            
            # Temporarily change the path to the new one
            old_path = os.environ['PATH']
            os.environ['PATH'] = '%s:%s' % (project.bin_path(), old_path)
            try:
                self.run_pip_install(project.bin_path, temp_reqs_path)
            except InstallationError:
                # Exit if any problems occur during installation
                self.logger.error('Installation could not be completed. '
                        'Aborting')
                sys.exit(2)
            finally:
                logger.debug('Removing temporary requirements file')
                os.remove(temp_reqs_path)
            os.environ['PATH'] = old_path
        requirements_path = project.path('requirements.txt')
        requirements_file = open(requirements_path, 'w')
        requirements_file.write(requirements_string)
        requirements_file.close()

    def run_pip_install(self, bin_path_resolver, requirements_file):
        # Run pip to install packages
        pip_bin = bin_path_resolver('pip')
        pip_command = 'install'
        self.logger.info('Running pip at %s' % pip_bin)
        return_code = call([pip_bin, pip_command, "-r", 
                requirements_file])
        if return_code != 0:
            raise InstallationError('An error occured during installation')

    def create_quickactivate_script(self, project):
        """Create a quickactivate script"""
        self.logger.info('Creating quick activate script')
        quick_activate_path = project.path('quickactivate.sh')
        quick_activate = open(quick_activate_path, 'w')
        quick_activate.write("source")
        quick_activate.close()

commands.register(InitializeCommand)
