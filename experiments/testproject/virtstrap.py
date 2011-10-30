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
import tarfile
import json
import os, sys
import platform
import urllib
import logging

# Only ever keep the latest log of warnings
logging.basicConfig(filename=".virtstrap.log", 
        level=logging.INFO, filemode="w")
# All logs will be sent to this logger
vs_logger = logging.getLogger("virtstrap")

BROWNIE_AVAILABLE = True
try:
    from brownie.terminal import TerminalWriter
except ImportError:
    BROWNIE_AVAILABLE = False

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
DEFAULT_PROFILE = "default"
RESOURCES_VERSION = "0.1"
RESOURCES_DIR_NAME = "virtstrap"

##########################################
# Program Options                        #
##########################################
parser = OptionParser()
parser.add_option("-n", "--no-build", dest="no_build",
        action="store_true",
        help="Only setup virtual environment")
parser.add_option("-d", "--base-dir", dest="virtstrap_base_dir",
        help="Set VirtStrap directory. Overrides setting in config", 
        default=None)
parser.add_option("-c", "--config", dest="config",
        help=("Install config defaults to {0}"
            .format(DEFAULT_CONFIG_FILENAME)), 
        default=DEFAULT_CONFIG_FILENAME)
parser.add_option("-p", "--profile", dest="profile",
        help=("Profile defaults to {0}".format(DEFAULT_PROFILE)), 
        default=DEFAULT_PROFILE)
parser.add_option("--resources-url", dest="virtstrap_resources_url",
        help="Set VirtStrap Resources Url. Overrides setting in config",
        default=None)
parser.add_option("--config-dir", dest="virtstrap_config_dir",
        help="Set VirtStrap Config Directory. Overrides setting in config",
        default=None)
parser.add_option("--force-download", dest="force_download",
        action="store_true",
        help="Force download the resources. Even if they exist")
parser.add_option("-i", "--interactive", dest="interactive",
        action="store_true",
        help="Turns on interactivity", 
        default=False)
parser.add_option("-v", "--verbose", dest="verbose",
        action="store_true",
        help="Turns on verbose output", 
        default=False)
parser.add_option("-q", "--quiet", dest="quiet",
        action="store_true",
        help="Turns on quiet output", 
        default=False)

cli_options, cli_args = parser.parse_args() #Global options and args

###########################################
# Special VirtStrap Console Log Handler   #
###########################################
class VirtStrapConsoleLogHandler(logging.Handler):
    def __init__(self, outputter):
        self._outputter = outputter
        logging.Handler.__init__(self)

    def emit(self, record):
        outputter = self._outputter 
        outputter.write(record.msg, record.levelname)

class ConsoleLogOutputter(object):
    def write(self, out, level):
        print(out)

class BrownieConsoleLogOutputter(ConsoleLogOutputter):
    level_colors = {
        "DEBUG": "green",
        "INFO": "black",
        "WARNING": "yellow",
        "CRITICAL": "purple",
        "ERROR": "red",
        "EXCEPTION": "red",
    }
    def __init__(self):
        self.terminal_writer = TerminalWriter(stream=sys.stdout)

    def write(self, out, level):
        color = self.level_colors.get(level, "black")
        self.terminal_writer.writeline(out, text_colour=color)

class Path(object):
    def __init__(self, path, base_path="./"):
        base_path_value = base_path
        if callable(base_path):
            base_path_value = base_path()
        base_path_value = str(base_path_value)
        self._base_path = base_path_value
        self._rel_path = os.path.relpath(os.path.join(base_path_value, path))
        self._abs_path = os.path.abspath(self._rel_path)

    @property
    def rel_path(self):
        return self._rel_path

    @property
    def abs_path(self):
        return self._abs_path

    def join(self, path):
        return Path(path, base_path=self)

    def __str__(self):
        return self._abs_path

    def __repr__(self):
        return 'Path("{0}")'.format(self._abs_path)

class AbstractOption(object):
    def parse(self, raw_value):
        return raw_value

    def get_default(self):
        return None

    def is_required(self):
        return False

class Option(AbstractOption):
    _option_count = 0
    def __init__(self, default=None, required=False):
        self.default = default
        self.required = required
        # A way to order the settings
        self._order = self.__class__._option_count
        self.__class__._option_count += 1

    def parse(self, raw_value):
        return raw_value

    def get_default(self):
        default = self.default
        if callable(default):
            return default()
        return default

    def is_required(self):
        return self.required

class StrOption(Option):
    pass

class BooleanOption(Option):
    def parse(self, raw_value):
        if type(raw_value) == "bool":
            return raw_value
        if raw_value in ["true", "True"]:
            return True
        elif raw_value in ["false", "False"]:
            return False
        raise CannotParseOption(
            "'{0}' is an unknown value to Boolean Option".format(raw_value))

class PathOption(Option):
    def __init__(self, base_path="./", **kwargs):
        self.base_path = base_path
        super(PathOption, self).__init__(**kwargs)

    def parse(self, raw_value):
        return Path(raw_value, base_path=self.base_path)

    def get_default(self):
        default = super(PathOption, self).get_default()
        if default is None:
            return None
        return Path(default, base_path=self.base_path)

class CLIWrap(AbstractOption):
    """An option that uses value from command line as override"""
    def __init__(self, cli_value=None, option=Option):
        self.cli_value = cli_value
        self.option = option

    def parse(self, raw_value):
        value_to_parse = raw_value
        if self.cli_value is not None:
            value_to_parse = self.cli_value
        return self.option.parse(value_to_parse)

    def get_default(self):
        return self.option.get_default()

    def is_required(self):
        return self.option.is_required()

class ListOption(Option):
    """Parses a list of values separated by line"""
    def parse(self, raw_value):
        return map(str.strip, raw_value.splitlines())

class SectionSettingsMeta(type):
    def __new__(meta, name, bases, cls_dict):
        options = {}
        default_values = {}
        cls_items = cls_dict.items()
        for key, value in cls_items:
            if isinstance(value, AbstractOption):
                options[key] = value
                default_values[key] = value.get_default()
                del cls_dict[key]
        cls_dict['_meta'] = dict(options=options)
        cls_dict['_defaults'] = default_values
        return type.__new__(meta, name, bases, cls_dict)

class ConfigError(Exception):
    def __init__(self, errors, section, *args, **kwargs):
        self.errors = errors
        self._section = section
        super(ConfigError, self).__init__("Settings have {0} error(s)"
                .format(len(errors)))

    def display_errors(self):
        vs_logger.error("Errors in section [{0}]".format(self._section))
        for error in self.errors:
            vs.logger.error("---{0}".format(error))

class SectionSettings(object):
    __metaclass__ = SectionSettingsMeta
    
    def __init__(self, **kwargs):
        self._errors = []
        self._validated = False
        data = self._defaults.copy()
        self._data = data
        self.apply_settings(kwargs)

    def __getattr__(self, name):
        if not self._validated:
            self._validate()
        if not self._data.has_key(name):
            return self.__attempt_to_access_property(name)
        value = self._data.get(name)
        return value

    def __attempt_to_access_property(self, name):
        # TODO Hacky fix at best. Will fix later 
        cls_dict = self.__class__.__dict__
        cls_item = cls_dict.get(name)
        if not isinstance(cls_dict[name], property):
            raise AttributeError("{0} not found".format(name))
        return cls_item.__get__(self)

    def _validate(self):
        errors = []
        option_parsers = self._meta['options']
        for key, option in option_parsers.iteritems():
            validate_value = getattr(self.__class__, 
                    "validate_{0}".format(key), lambda instance, data: data)
            validate_value(self, self._data)
            value = self._data.get(key)
            if not value and option.is_required():
                errors.append('Option "{0}" is required'.format(key))
        if errors:
            raise ConfigError(errors, self.__section__)
        self._errors = errors
        self._validated = True

    def _set_data(self, key, value):
        self._data[key] = value

    @classmethod
    def parse(cls, section_data):
        section_data = section_data or {}
        settings = cls(**section_data)
        try:
            settings._validate()
        except ConfigError, e:
            e.display_errors()
        return settings

    def apply_settings(self, section_data):
        # Get the option parsers
        option_parsers = self._meta['options']
        # Parse incoming data
        parsed_section_data = {}
        for key, value in section_data.iteritems():
            parser = option_parsers.get(key)
            if not parser:
                # this isn't data we know do not store it
                continue
            parsed_section_data[key] = parser.parse(value)
        self._data.update(parsed_section_data)

class VirtStrapSectionSettings(SectionSettings):
    __section__ = "virtstrap"
    base_dir = PathOption(default="vs.env/")
    resources_url = Option(default=(
        "https://github.com/ravenac95/virtstrap-resources/tarball/master"))
    config_dir = PathOption(default="conf/")
    
    @property
    def resources_dir(self):
        return Path(RESOURCES_DIR_NAME, base_path=self.base_dir)

    @property
    def packages_dir(self):
        return Path("packages", base_path=self.resources_dir)

    @property
    def virtstrapext_dir(self):
        return Path("virtstrapext", base_path=self.packages_dir)

    @property
    def bin_path(self):
        return Path("bin", base_path=self.base_dir)


class ProjectSectionSettings(SectionSettings):
    __section__ = "project"
    name = Option(required=True)
    project_dir = PathOption()
    
    def validate_project_dir(self, data):
        if not data['project_dir']:
            data['project_dir'] = data['name']
        return data

    @property
    def root_dir(self):
        """Get the project's root directory (this directory)"""
        return Path(os.path.abspath(os.path.dirname(__file__)))

class VirtStrapSettings(object):
    def __init__(self, sections_data, profile=DEFAULT_PROFILE):
        self._sections_data = sections_data # Raw Section Data
        self._sections = {} # Parsed Section Data
        self._profile = profile

    @classmethod
    def parse_from_file(cls, filename, profile, virtstrap_override=None):
        virtstrap_override = virtstrap_override or None
        # Try opening the settings file
        try:
            settings_file = CommentlessFile(filename)
        except IOError:
            #If file isn't found tell the user and exit with error
            vs_logger.error("A settings file is required. Could not find {0}"
                    .format(filename))
            exit_with_error()
        # Parse the configuration
        config = ConfigParser.ConfigParser()
        config.readfp(settings_file)

        # Collect the installation sections
        # into a dict of dicts
        sections_data = {}
        all_sections = config.sections()
        for section in all_sections:
            section_data = dict(config.items(section))
            sections_data[section] = section_data
        settings = cls(sections_data, profile=profile)
        # Parse virtstrap Section
        settings.parse_section(VirtStrapSectionSettings, 
                override=virtstrap_override)
        # Parse the project section
        settings.parse_section(ProjectSectionSettings)
        return settings
    
    def _compile_section_data(self, section_name):
        """
        Combines profile settings and default config. 
        Profile overrides default.
        """
        # Get default data if any
        default_section_data = self._sections_data.get(section_name, {})
        section_data = default_section_data.copy()
        # Get the profile data
        # you need to grab the key first
        current_profile = self._profile
        # if the profile is just the default then no need to get the profile
        section_profile_data = {}
        if current_profile != DEFAULT_PROFILE:
            # Compute the profile key
            section_profile_key = "{0}:{1}".format(section_name, 
                    current_profile)
            # Get the data
            section_profile_data = self._sections_data.get(
                    section_profile_key, {})
        # Override the default data with the profile data
        section_data.update(section_profile_data)
        return section_data

    def get_section(self, section_name):
        return self._sections.get(section_name, None)

    def parse_section(self, section_settings, override=None):
        override = override or {}
        section_name = section_settings.__section__
        section_data = self._compile_section_data(section_name)
        section_data.update(override)
        parsed_section = section_settings.parse(section_data)
        self._sections[section_name] = parsed_section

    def __getattr__(self, name):
        section = self.get_section(name)
        if not section:
            raise AttributeError("Section {0} does not exist or is unparsed"
                    .format(name))
        return section

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
    vs_logger.error("Exiting. virtstrap task incomplete.")
    sys.exit(EXIT_WITH_ERROR)

def exit_normally():
    vs_logger.info("virtstrap task completed successfully")
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

# Create a download utility
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
    if not cli_options.interactive:
        exit_with_error()
    else:
        if yes_no_input("Skip?"):
            vs_logger.info("Skipping.")
        else:
            exit_with_error()

def all_paths_exist(paths):
    for path in paths:
        if not os.path.exists(str(path)):
            return False
    return True

def download_file(url, destination, skip_allowed=False):
    urlopener = VSURLOpener()
    retries = 0
    downloaded = False
    vs_logger.info("Downloading {0} to {1}".format(url, destination))
    while retries < MAX_DOWNLOAD_RETRIES:
        try:
            urlopener.retrieve(url, destination)
        except HTTPError, e:
            vs_logger.exception(e.error_code)
        else:
            downloaded = True
            break
        retries += 1
        if retries < MAX_DOWNLOAD_RETRIES:
            vs_logger.info("Retrying")
    if not downloaded:
        vs_logger.warning("Failed to download {0}".format(url))
        if skip_allowed:
            ask_to_skip()
            return False
        else:
            exit_with_error()
    vs_logger.info("Completed download of {0}".format(destination))
    return True

class SuspiciousTarball(Exception):
    pass

class FileNotDownloaded(Exception):
    pass

class TarballDownloader(object):
    """Downloads and unpacks tar.gz files"""
    def __init__(self, url, destination, unpack_destination=None, 
            change_root=None, compression="*"):
        self._change_root = change_root
        self._url = url
        self._destination = destination
        self._unpack_destination = unpack_destination or destination
        self._compression = compression

    def download_and_unpack(self, skip_allowed=False):
        self._download(skip_allowed=skip_allowed)
        self._unpack()

    def unpack_only(self):
        self._unpack()

    def _unpack(self):
        # Unpack the files
        # First open the tarball
        mode = "r:{0}".format(self._compression)
        tarball = tarfile.open(self._destination, mode)
        # Get the names of the files in the tarball
        names = tarball.getnames()
        # assume the first name is the root of the tarball
        root = names[0]
        # then check the names for safety 
        map(lambda name: self._check_tarball_name(name, root),
                names)
        # Gather tarball members
        members = tarball.getmembers()
        # if user wants to change the root then change the root
        if self._change_root:
            self._change_members_roots(members, root, self._change_root)
        # unpack to the destination
        unpack_destination = self._unpack_destination
        tarball.extractall(path=unpack_destination, members=members[1:])

    def _change_members_roots(self, members, old_root, new_root):
        for member in members:
            old_path = member.path
            new_path = old_path.replace(old_root, new_root, 1)
            member.path = new_path

    def _check_tarball_name(self, name, root):
        if name.startswith(".."):
            raise SuspiciousTarball(
                    "Tarball has reference to the parent directory.")
        if name.startswith("/"):
            raise SuspiciousTarball(
                    "Tarball has reference to the root directory.")
        if name.startswith("."):
            raise SuspiciousTarball(
                    "Tarball has reference to the current directory.")
        if not name.startswith(root):
            raise SuspiciousTarball(
                    "Tarball doesn't have common root.")
        return True

    def _download(self, skip_allowed=False):
        url = self._url
        destination = self._destination
        downloaded = download_file(url, destination, 
                skip_allowed=skip_allowed)
        # Check if the file was downloaded
        if not downloaded:
            raise FileNotDownloaded()


##########################################
# VirtStrap Class                        #
##########################################

# VirtStrap Errors
class CorruptedResourcesPackage(Exception):
    pass

class VirtStrap(object):
    def __init__(self, options, args):
        self.settings = None
        self._options = options
        self._args = args

    def run(self):
        """Runs the current virtstrap command"""
        try:
            # Prepare the settings
            self._parse_basic_settings()
            # Create the base dir
            self._create_virtstrap_dirs()
            # Download and unpack the resources
            self._download_and_unpack_resources()
            # Setup sys.path with new resources
            self._setup_resources_in_sys_path()
            # Run the command
            self._execute_command()
        except:
            vs_logger.exception("Error executing virtstrap. Check .virtstrap.log for details")
            exit_with_error()
    
    def _get_virtstrap_settings(self):
        return self.settings.virtstrap
        
    def _parse_basic_settings(self):
        """Parses project and virtstrap settings"""
        options = self._options
        args = self._args
        config_file_path = os.path.abspath(options.config)
        vs_logger.info('Using configuration at "{0}"'.format(config_file_path))
        # Compile a dict of overrides from the options
        options_override = self._build_virtstrap_settings_override()
        # Initialize the settings
        settings = VirtStrapSettings.parse_from_file(config_file_path, 
                options.profile, virtstrap_override=options_override)
        # Save the settings
        self.settings = settings

    def _build_virtstrap_settings_override(self):
        """Builds a dict of values to override the config file settings"""
        opts_to_settings_mapping = [
            ("virtstrap_base_dir", "base_dir"),
            ("virtstrap_resources_url", "resource_url"),
            ("virtstrap_config_dir", "virtstrap_config_dir"),
        ]
        options = self._options
        override = {}
        for opt_key, settings_key in opts_to_settings_mapping:
            opt_value = getattr(options, opt_key)
            if opt_value is not None:
                override[opt_key] = opt_value
        return override

    def _create_virtstrap_dirs(self):
        """Create the virtstrap directory and necessary child directories"""
        # Try to make the directory for virtstrap
        virtstrap_settings = self._get_virtstrap_settings()
        virtstrap_base_dir = virtstrap_settings.base_dir.abs_path
        if os.path.isdir(virtstrap_base_dir):
            vs_logger.info('Using already built virtstrap base directory at "{0}"'
                .format(virtstrap_base_dir))
        else:
            vs_logger.info('Creating virtstrap base directory at "{0}"'
                    .format(virtstrap_base_dir))
            try:
                os.mkdir(virtstrap_base_dir)
            except OSError, e:
                vs_logger.exception("Failed to create virtstrap base directory")
                raise

    def _download_and_unpack_resources(self):
        options = self._options
        force_download = options.force_download
        virtstrap_settings = self._get_virtstrap_settings()
        virtstrap_resources_url = virtstrap_settings.resources_url
        virtstrap_base_dir = virtstrap_settings.base_dir.abs_path
        # Check if the resources have been downloaded
        # the presence of the zip will suffice for now.
        virtstrap_resources_file_path = os.path.join(virtstrap_base_dir, 
                "resources.tar.gz")
        downloader = TarballDownloader(virtstrap_resources_url,
                virtstrap_resources_file_path, change_root=RESOURCES_DIR_NAME,
                unpack_destination=virtstrap_base_dir)
        if not os.path.isfile(virtstrap_resources_file_path) or \
                force_download:
            downloader.download_and_unpack()
        if not self._resources_verified():
            downloader.unpack_only()
            if not self._resources_verified():
                raise CorruptedResourcesPackage(
                    "The package of resources does not contain the necessary "
                    "files and directories for virtstrap to continue")
    
    def _resources_verified(self):
        virtstrap_settings = self._get_virtstrap_settings()
        paths = [
            virtstrap_settings.base_dir,
            virtstrap_settings.resources_dir,
            virtstrap_settings.packages_dir,
        ]
        return all_paths_exist(paths)

    def _setup_resources_in_sys_path(self):
        virtstrap_settings = self._get_virtstrap_settings()
        # Add virtstrap resources to the sys.path
        virtstrap_packages_dir = str(virtstrap_settings.packages_dir)
        sys.path.insert(0, virtstrap_packages_dir)

    def _execute_command(self):
        options = self._options
        args = self._args
        settings = self.settings
        try:
            from virtstrapcore import virtstrap_core
        except ImportError, e:
            vs_logger.exception("Resource files are missing virtstrapcore. "
                    "VirtStrap cannot continue")
            exit_with_error()
        virtstrap_core.initialize(options, args, settings)
        virtstrap_core.execute_command()
            
##########################################
# Main                                   #
##########################################
def main():
    outputter = ConsoleLogOutputter()
    if BROWNIE_AVAILABLE:
        outputter = BrownieConsoleLogOutputter()
    console_handler = VirtStrapConsoleLogHandler(outputter=outputter)
    console_handler.setLevel(logging.INFO)
    vs_logger.setLevel(logging.INFO)
    if cli_options.quiet:
        console_handler.setLevel(logging.WARNING)
        vs_logger.setLevel(logging.WARNING)
    if cli_options.verbose:
        console_handler.setLevel(logging.DEBUG)
        vs_logger.setLevel(logging.DEBUG)
    vs_logger.addHandler(console_handler)
    virtstrap = VirtStrap(cli_options, cli_args)
    virtstrap.run()
    exit_normally()

if __name__ == "__main__":
    main()
