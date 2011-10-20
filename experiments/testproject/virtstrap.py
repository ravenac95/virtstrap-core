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

DEFAULT_PACKAGE_SETTINGS = dict(
    name="",
    use_site_packages=False,
    virtualenv_dir="./vs.env/",
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
# Utility functions                      #
##########################################
def in_virtualenv():
    if hasattr(sys, 'real_prefix'):
        return True
    return False

def find_file_or_skip(file, not_found_string="'{0}' not found."):
    file_found = True
    if not os.path.isfile(file):
        file_found = False
        print not_found_string.format(file)
        if options.interactive:
            exit_with_error()
        else:
            if yes_no_input("Skip?"):
                print "Skipping."
            else:
                exit_with_error()
    return file_found

def find_all_files_or_skip(files, not_found_string="Files not found."):
    files_found = True
    if not all_files_exist(files):
        files_found = False
        print not_found_string
        if not options.interactive:
            exit_with_error()
        else:
            if yes_no_input("Skip?"):
                print "Skipping."
            else:
                exit_with_error()
    return files_found

def all_files_exist(files):
    for file in files:
        if not os.path.isfile(file):
            return False
    return True

def get_virtualenv_dir_abspath():
    return os.path.abspath(settings['virtualenv_dir'])

def make_current_settings(settings_filename, default_settings=None):
    # set default_settings
    if not default_settings:
        default_settings = DEFAULT_SETTINGS
    # Try opening the settings file
    try:
        settings_file = open(settings_filename)
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

    return current_settings, install_settings
    
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

def commands_installer(commands):
    try:
        shell_script_file = settings['shell_script_file']
    except KeyError:
        print "Shell Script env_type requires a setting 'command_list_file'"
        exit_with_error()
    if find_file_or_skip(shell_script_file):
        call(["sh", shell_script_file])

##########################################
# Script Commands                        #
##########################################

def bootstrap():
    """The default command for this script"""
    create_virtualenv()
    run_build()

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
    virtualenv_dir = settings['virtualenv_dir']
    virtualenv_dir_abspath = get_virtualenv_dir_abspath()
    print "Creating Virtual Environment in {0}".format(virtualenv_dir_abspath)
    virtualenv.create_environment(settings['virtualenv_dir'], 
            site_packages=settings['use_site_packages'], 
            prompt=settings['prompt'])
    # Create activation script
    print "Create quickactivate.sh script for virtualenv"
    quick_activation_script(virtualenv_dir_abspath)


def quick_activation_script(virtualenv_dir, file="quickactivate.sh", 
        base_path='./'):
    """Builds a virtualenv activation script shortcut"""
    quick_activate_filename = os.path.join(base_path, file)
    quick_activate_file = open(quick_activate_filename, 'w')
    quick_activate_file.writelines(["#!/bin/bash\n", 
        "source {0}/bin/activate".format(virtualenv_dir)])
    quick_activate_file.close()

def run_build():
    """Build the project based on the installation settings"""
    for setting_name, setting_raw_value in install_settings.iteritems():
        # Turn lines of settings values into an array of settings
        setting_values = setting_raw_value.splitlines() 
        # Grab the appropriate installer
        installer = INSTALLERS.get(setting_name)
        if not installer:
            print "Install config key '{0}' is unknown".format(setting_name)
            if not options.interactive:
                exit_with_error()
            else:
                if yes_no_input("Skip?"):
                    print "Skipping."
                else:
                    exit_with_error()
        installer(setting_values)

##########################################
# Program settings                       #
##########################################

VIRTSTRAP_COMMANDS = dict(
    default=bootstrap,
    build=run_build
)

INSTALLERS = dict(
    requirements=pip_requirements_installer,
    commands=commands_installer,
    environment=enviroment_installer
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
    global settings, install_settings
    settings, install_settings = make_current_settings(
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
