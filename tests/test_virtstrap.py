import os
from nose.tools import raises
from virtstrap.virtstrap import *

@raises(ConfigError)
def test_project_settings_with_no_settings():
    """Project settings with no settings"""
    # Create settings with no data
    settings = ProjectSectionSettings()
    # Try to access the data
    name = settings.name

def test_project_settings_with_no_settings_and_expected_errors():
    """
    Project settings with no settings and the expected count of errors
    """
    # Create settings with no data
    settings = ProjectSectionSettings()
    #ensure that the exception is called
    config_error_called = False
    # Try to access the data and there should only be one error
    try:
        name = settings.name
    except ConfigError, exc:
        config_error_called = True
        assert len(exc.errors) == 2
    assert config_error_called == True

def test_project_settings_minimum():
    """Project settings with minimum settings"""
    project_name = "project_name"
    settings = ProjectSectionSettings(name=project_name)
    #Verify all the settings are set correctly
    assert settings.name == project_name
    assert str(settings.project_dir) == os.path.abspath(project_name)
    #Ensure that none of the settings are 'None'
    for key, value in settings._data.iteritems():
        assert getattr(settings, key) is not None

def test_project_settings_minimum_using_parse_method():
    """Project settings with minimum settings with parse method"""
    project_name = "project_name"
    settings = ProjectSectionSettings.parse(dict(name=project_name))
    #Verify all the settings are set correctly
    assert settings.name == project_name
    assert str(settings.project_dir) == os.path.abspath(project_name)
    #Ensure that none of the settings are 'None'
    for key, value in settings._data.iteritems():
        assert getattr(settings, key) is not None

def test_project_settings_with_diff_project_name_and_project_dir():
    """Project settings with different project name and project directory"""
    project_name = "project_name"
    project_dir = "project_dir"
    settings = ProjectSectionSettings(name=project_name, 
            project_dir=project_dir)
    #Verify all the settings are set correctly
    assert settings.name == project_name
    assert str(settings.project_dir) == os.path.abspath(project_dir)
    #Ensure that none of the settings are 'None'
    for key, value in settings._data.iteritems():
        assert getattr(settings, key) is not None

def test_path():
    """Test that paths are calculated very rudimentary"""
    test_path = "base"
    base_path = "base"
    path = Path(test_path, base_path)
    # Test Rel Path
    assert path.rel_path.endswith(test_path)
    assert path.rel_path.find(base_path) != -1
    # Test Abs Path
    assert path.abs_path.endswith(test_path)
    assert path.abs_path.find(base_path) != -1

def test_list_option():
    """Test ListOption parses lines into values"""
    list_option = ListOption()
    parsed_list = list_option.parse("line1\nline2\n    line3")
    assert parsed_list == ['line1', 'line2', 'line3']

TEST_SECTION_DATA1 = {
    "project": {
        "name": "project_name"
    },
    "someothersection:profile": {
        "key": "value"
    }
}

@raises(AttributeError)
def test_virtstrap_settings_no_parsing():
    """Test virtstrap settings when you don't parse"""
    application_settings = VirtStrapSettings(TEST_SECTION_DATA1)
    project_settings = application_settings.project

def test_virtstrap_settings_parsed():
    """Test virtstrap setting when it's parsed"""
    application_settings = VirtStrapSettings(TEST_SECTION_DATA1)
    # Parse project settings
    application_settings.parse_section(ProjectSectionSettings)
    project_settings = application_settings.project
    assert project_settings.name == TEST_SECTION_DATA1['project']['name']

TEST_BASIC_FILE = """
[project]
name = test_project_file # This is the most basic setting necessary
"""

class TempConfigFile(object):
    @classmethod
    def create_with_contents(cls, contents):
        temp_config_file = cls()
        temp_config_file.write_contents(contents)
        return temp_config_file

    def __init__(self):
        self._filename = None

    def write_contents(self, contents):
        temp_file = open(self.filename, 'w')
        temp_file.write(contents)
        temp_file.close()

    def delete_file(self):
        if self._filename is not None:
            os.remove(self._filename)
        self._filename = None

    def _make_temp_file(self):
        import tempfile
        temp = tempfile.mkstemp()
        temp_filename = temp[1]
        self._filename = temp_filename

    @property
    def filename(self):
        if self._filename is None:
            self._make_temp_file()
        return self._filename

def create_virtstrap_settings_from_temp_file(contents, profile):
    temp_config_file = TempConfigFile.create_with_contents(contents)
    settings = VirtStrapSettings.parse_from_file(temp_config_file.filename, 
            profile)
    # Parse virtstrap section
    settings.parse_section(VirtStrapSectionSettings)
    # Parse project section
    settings.parse_section(ProjectSectionSettings)
    temp_config_file.delete_file()
    return settings

def test_virtstrap_settings_parse_file():
    """Parse a settings file using default profile"""
    settings = create_virtstrap_settings_from_temp_file(TEST_BASIC_FILE, 
            "default")
    assert settings.project.name == "test_project_file"

TEST_MULTISECTION_FILE = """
[project]
name = test_project_file # This is the most basic setting necessary

[environment]
pre_script = script1
post_script = script2
"""

class EnvironmentSectionSettings(SectionSettings):
    __section__ = "environment"
    pre_script = Option()
    post_script = Option()

def test_virtstrap_settings_parse_file_with_additional_section():
    """Parse a settings file using default profile and additional section"""
    settings = create_virtstrap_settings_from_temp_file(TEST_MULTISECTION_FILE, 
            "default")
    settings.parse_section(EnvironmentSectionSettings)
    assert settings.project.name == "test_project_file"
    assert settings.environment.pre_script == "script1"
    assert settings.environment.post_script == "script2"

TEST_PRODUCTION_PROFILE_FILE = """
[project]
name = test_project_file # This is the most basic setting necessary

[environment:production]
pre_script = script1
post_script = script2
"""

def test_virtstrap_settings_parse_file_using_production_profile():
    settings = create_virtstrap_settings_from_temp_file(
            TEST_PRODUCTION_PROFILE_FILE, "production")
    settings.parse_section(EnvironmentSectionSettings)
    assert settings.project.name == "test_project_file"
    assert settings.environment.pre_script == "script1"
    assert settings.environment.post_script == "script2"
