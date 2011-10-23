#!/usr/bin/env python
#coding=utf-8
"""
VirtualEnvironment Bootstrap
============================

zc.buildout is a great system for many different purposes. However,
for quick prototyping of libraries and flexibility of using easy_install
or pip virtualenv has the edge on buildout. The one major function that 
virtualenv does not have is easy repeatability. This script attempts
to remedy that by creating a special bootstrap for virtualenv that has the
ability to use pip requirements and shell scripts to introduce repeatability 
to your programs and packages.
"""
from optparse import OptionParser
import ConfigParser
from subprocess import call
import json
import os, sys
import imp
import platform
import urllib

VIRTUALENV_INSTALLED = True
try:
    import virtualenv
except ImportError:
    VIRTUALENV_INSTALLED = False

if platform.system() == "Windows":
    print "virtstrap is only made for posix systems. Sorry."
    sys.exit(1)

##########################################
# Program Constants                      #
##########################################
EXIT_WITH_ERROR = 1
EXIT_NORMALLY = 0
VIRTUALENV_PROMPT_TEMPLATE = "({0}env) "
DEFAULT_CONFIG_FILENAME = "conf/proj.cfg"
MAX_DOWNLOAD_RETRIES = 3

DEFAULT_PROJECT_SETTINGS = dict(
    name="",
    dir="",
    config_dir="conf",
    conf_module_base="virtstrapconf",
    use_site_packages=False,
    virtualenv_dir="./vs.env/",
    virtstrap_base_url=
        "https://raw.github.com/ravenac95/virtstrap/master/virtstrap/",
)

##########################################
# Command line input functions           #
##########################################
def yes_no_input(prompt, default=True):
    default_input_string = "[Y/n]"
    if not default:
        default_input_string = "[y/N]"
    while True:
        raw_result = raw_input_with_default(prompt, default_input_string)
        if not raw_result.lower() in ["yes", "no", "y", "n"]:
            print "Please only input yes, no, y, or n"
        else:
            if raw_result.startswith('y'):
                result = True
            else:
                result = False
            break
    return result

def raw_input_with_default(prompt, default_input_string="['']"):
    return raw_input("{0} {1}:".format(prompt, default_input_string))

##########################################
# Exit functions                         #
##########################################
def exit_with_error():
    print "Exiting. virtstrap task incomplete."
    sys.exit(EXIT_WITH_ERROR)

def exit_normally():
    print "virtstrap task completed."
    sys.exit(EXIT_NORMALLY)

##########################################
# CommentlessFile                        #
##########################################

class CommentlessFile(file):
    def readline(self):
        line = super(CommentlessFile, self).readline()
        if line:
            line = line.split('#', 1)[0].rstrip()
            line = line.split(';', 1)[0].rstrip()
            return line + '\n'
        else:
            return ''

##########################################
# Utility classes                        #
##########################################

#Create a download utility
class HTTPError(Exception):
    def __init__(self, url, fp, error_code, error_msg, headers):
        self.url = url
        self.fp = fp
        self.error_code = error_code
        self.error_msg = error_msg
        self.headers = headers

class VSURLOpener(urllib.FancyURLopener):
    def http_error_default(self, url, fp, error_code, 
            error_msg, headers):
        raise HTTPError(url, fp, error_code, error_msg, headers)

##########################################
# Utility functions                      #
##########################################
def in_virtualenv():
    if hasattr(sys, 'real_prefix'):
        return True
    return False

def ask_to_skip():
    if not options.interactive:
        exit_with_error()
    else:
        if yes_no_input("Skip?"):
            print "Skipping."
        else:
            exit_with_error()

def find_file_or_skip(file, not_found_string="'{0}' not found."):
    file_found = True
    if not os.path.isfile(file):
        file_found = False
        print not_found_string.format(file)
        ask_to_skip()
    return file_found

def find_all_files_or_skip(files, not_found_string="Files not found."):
    files_found = True
    if not all_files_exist(files):
        files_found = False
        print not_found_string
        ask_to_skip()
    return files_found

def all_files_exist(files):
    for file in files:
        if not os.path.isfile(file):
            return False
    return True

def get_virtualenv_dir():
    return settings['virtualenv_dir']

def get_virtualenv_dir_abspath():
    return settings['virtualenv_dir_abspath']

def resource_local_path(file_path=""):
    virtstrap_resource_dir = settings['virtstrap_resource_dir']
    return os.path.join(virtstrap_resource_dir, file_path)

def resource_remote_url(file_path=""):
    base_url = settings['virtstrap_base_url']
    return os.path.join(base_url, file_path)

def download_file(url, destination, skip_allowed=False):
    urlopener = VSURLOpener()
    retries = 0
    while retries < MAX_DOWNLOAD_RETRIES:
        try:
            urlopener.retrieve(url, destination)
        except HTTPError, e:
            print e.error_code
        else:
            break
        retries += 1
        if retries < MAX_DOWNLOAD_RETRIES:
            print "Retrying"
    print "Failed to download {0}".format(url)
    if skip_allowed:
        ask_to_skip()
    else:
        exit_with_error()

def download_resource_file(file_path):
    url = resource_remote_url(file_path)
    destination = resource_local_path(file_path)
    print 'Downloading resource "{0}"'.format(file_path)
    download_file(url, destination)

def make_current_settings(settings_filename, default_settings=None):
    # set default_settings
    if not default_settings:
        default_settings = DEFAULT_PROJECT_SETTINGS
    # Try opening the settings file
    try:
        settings_file = CommentlessFile(settings_filename)
    except IOError:
        #If file isn't found tell the user and exit with error
        print ("A settings file is required. Could not find {0}"
                .format(settings_filename))
        exit_with_error()
    # Parse the configuration
    config = ConfigParser.ConfigParser()
    config.readfp(settings_file)
    
    # Copy defaults into a new settings dictionary
    current_settings = default_settings.copy()
    
    # Get all the project settings
    project_settings = dict(config.items("project"))

    # Update the defaults with the current project settings
    current_settings.update(project_settings)

    # Ensure that the settings define a package name
    package_name = current_settings.get("name")
    if not package_name:
        #If there isn't a package name then tell user and exit with error
        print "At least a package name is required for virtstrap.py"
        exit_with_error()

    # Create the default virtualenv prompt using the package name
    prompt = VIRTUALENV_PROMPT_TEMPLATE.format(package_name)
    current_settings['prompt'] = prompt
    current_settings['virtualenv_dir_abspath'] = os.path.abspath(
            current_settings['virtualenv_dir'])
   
    # Create setting for virtstrap resource directory
    virtstrap_resource_dir = os.path.join(
            current_settings['virtualenv_dir_abspath'], "virtstrap")
    current_settings['virtstrap_resource_dir'] = virtstrap_resource_dir

    # Collect the installation sections
    all_sections = config.sections()
    installation_profiles = dict()
    for section in all_sections:
        if section.startswith("install"):
            install_section_list = section.split(":")
            try:
                profile = install_section_list[1]
            except IndexError:
                profile = "default"
            install_section_dict = dict(config.items(section))
            installation_profiles[profile] = install_section_dict
    
    selected_install_profile = options.install_profile
    install_settings = installation_profiles.get(
            selected_install_profile)

    if not install_settings:
        print "{0} is not a defined installation_profile.".format(
                selected_install_profile)
        exit_with_error()

    #Collect environment settings
    environment_settings = dict()

    return current_settings, install_settings, environment_settings
    
##########################################
# Installer commands                     #
##########################################

def pip_requirements_installer(requirements_files):
    """Builds pip requirements"""
    virtualenv_dir_abspath = get_virtualenv_dir_abspath()
    
    for requirements_file in requirements_files:
        if find_file_or_skip(requirements_file):
            pip_bin = "{0}/bin/pip".format(
                    virtualenv_dir_abspath)
            pip_command = "install"
            call([pip_bin, pip_command, "-r", requirements_file])

def scripts_installer(scripts):
    config_directory = settings['config_dir']
    conf_module_base = settings['conf_module_base']
    #execute scripts
    for script in scripts:
        #execute script
        script_path = os.path.join(config_directory, script)
        script_module_name = script.split(".")[0]
        conf_module_path = "_".join([conf_module_base, script_module_name])
        try:
            script_module = imp.load_source(conf_module_path, script_path)
        except ImportError:
            print 'Script at "{0}" not found'.format(script_path)
            ask_to_skip()
        else:
            script_module.script_run(settings)
        

##########################################
# Script Commands                        #
##########################################

def bootstrap():
    """The default command for this script"""
    create_virtualenv()
    run_build()

def download_resources():
    #Download virtstrap resources
    files_to_download = ('env.py', 'templates/quickactivate.sh')

def create_virtualenv():
    """Create the virtual environment"""
    if not VIRTUALENV_INSTALLED:
        message = ("In order to bootstrap with virtstrap. "
                "You need virtualenv installed and you "
                "should not be in an active virtualenv")
        print message
        exit_with_error()
    if in_virtualenv():
        message = ("WARNING: You are currently in an active virtualenv. "
                "This is highly discouraged.")
        print message
        exit_with_error()
    # Create a virtual environment directory
    virtualenv_dir = get_virtualenv_dir()
    virtualenv_dir_abspath = get_virtualenv_dir_abspath()
    print "Creating Virtual Environment in {0}".format(virtualenv_dir_abspath)
    virtualenv.create_environment(virtualenv_dir,
            site_packages=settings['use_site_packages'], 
            prompt=settings['prompt'])
    # Create activation script
    activate_template = "quickactivate.sh.tmpl"
    # Download template if necessary
    if not all_files_exist([resource_local_path(activate_template)]):
        download_resource_file(activate_template)
    # Add virtstrap resources to the sys.path
    virtstrap_packages_dir = resource_local_path("packages")
    sys.path.insert(0, virtstrap_packages_dir)

    # Build the file from the template
    print "Creating quickactivate.sh script for virtualenv"
    quick_activation_script(virtualenv_dir_abspath)


def quick_activation_script(virtualenv_dir, 
        template_filename="quickactivate.sh.tmpl", 
        output_filename="quickactivate.sh", base_path='./'):
    import tempita
    """Builds a virtualenv activation script shortcut"""
    # Load Template
    quick_activate_template = tempita.Template.from_filename(
            resource_local_path(template_filename))
    # Prepare template context
    context = settings.copy()
    context['environment'] = environment_settings
    # Render template to string
    output_string = quick_activate_template.substitute(context)
    # Open output file for writing
    quick_activate_filename = os.path.join(base_path, output_filename)
    quick_activate_file = open(quick_activate_filename, 'w')
    # Write to the file
    quick_activate_file.write(output_string)
    quick_activate_file.close()

def run_build():
    """Build the project based on the installation settings"""
    old_path = os.environ['PATH']
    virtualenv_dir = settings['virtualenv_dir']
    virtualenv_bin_path = os.path.abspath(os.path.join(virtualenv_dir, "bin"))
    os.environ['PATH'] = "{0}:{1}".format(virtualenv_bin_path, old_path)
    for setting_name, setting_raw_value in install_settings.iteritems():
        # Turn lines of settings values into an array of settings
        setting_values = setting_raw_value.splitlines() 
        # Grab the appropriate installer
        installer = INSTALLERS.get(setting_name)
        if not installer:
            print "Install config key '{0}' is unknown".format(setting_name)
            ask_to_skip()
        installer(setting_values)
    os.environ['PATH'] = old_path

##########################################
# Program settings                       #
##########################################

VIRTSTRAP_COMMANDS = dict(
    default=bootstrap,
    build=run_build
)

INSTALLERS = dict(
    requirements=pip_requirements_installer,
    scripts=scripts_installer,
    #environment=enviroment_installer
)

parser = OptionParser()
parser.add_option("-n", "--no-build", dest="no_build",
        help="Only setup virtual environment")
parser.add_option("-c", "--config", dest="config",
        help=("Install config defaults to {0}"
            .format(DEFAULT_CONFIG_FILENAME)), 
        default=DEFAULT_CONFIG_FILENAME)
parser.add_option("-p", "--install-profile", dest="install_profile",
        help=("Install profile defaults to default"), 
        default="default")
parser.add_option("-i", "--interactive", dest="interactive",
        help="Turns on interactivity", 
        default=False)

options, args = parser.parse_args() #Global options and args

settings = None # Global settings for the script
install_settings = None # Global installation profiles
environment_settings = None # Environment Settings

##########################################
# Main                                   #
##########################################
def main():
    # If there aren't args set command to default
    if len(args) == 0:
        command_name = "default"
    else:
        # Otherwise use the first argument as the command
        command_name = args[0]
    # Compile settings and installation_profiles into global settings variable
    global settings, install_settings, environment_settings
    settings, install_settings, environment_settings = make_current_settings(
            options.config)

    # Choose virtstrap command from dictionary of commands
    virtstrap_command = VIRTSTRAP_COMMANDS.get(command_name)

    # If the virtstrap command doesn't exist then exit with error
    if not virtstrap_command:
        print "'{0}' is not a valid command".format(command_name)
        exit_with_error()
    virtstrap_command()
    exit_normally()

if __name__ == "__main__":
    main()
