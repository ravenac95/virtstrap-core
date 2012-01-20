"""
VirtstrapConfig
===============

VirtstrapConfig is an interface to the VEfile. It collects the VEfile's 
settings between all the applicable profiles.
"""
import yaml

class ConfigurationError(Exception):
    pass

class ConfigurationCompilationError(Exception):
    pass

class VirtstrapConfig(object):
    @classmethod
    def from_string(cls, string):
        config = cls()
        config.parse(string)
        return config

    @classmethod
    def from_file(cls, filename):
        string = open(filename)
        return cls.from_string(string)

    def parse(self, string):
        raw_config_data = yaml.load_all(string)
        profile_data = {}
        for profile in raw_config_data:
            profile_name = profile.get('profile', 'default')
            if profile_name in profile_data:
                raise ConfigurationError('Profile "{0}" found again. Cannot '
                        'have the same profile multiple times'
                        .format(profile_name))
            profile_data[profile_name] = profile
        self._raw_profile_data = profile_data
                
    def section(self, section_name, profiles=None):
        # The default profile is ALWAYS processed no exceptions
        profiles_to_compile = ['default']
        # Add the other profiles to the process. 
        profiles_to_compile.extend(profiles or [])
        raw_profile_data = self._raw_profile_data
        # process all of the profiles requested
        compiled_data = None
        for profile in profiles_to_compile:
            profile_data = raw_profile_data.get(profile, None)
            section_data = profile_data.get(section_name, None)
            if section_data:
                if compiled_data and type(compiled_data) != type(section_data):
                    raise ConfigurationCompilationError('Sections contain '
                            'incompatible data. '
                            'You cannot mix a list and a dict')
                if isinstance(compiled_data, dict):
                    compiled_data.update(section_data)
                elif isinstance(compiled_data, list):
                    compiled_data.extend(section_data)
                else:
                    if isinstance(section_data, dict):
                        compiled_data = section_data.copy()
                    elif isinstance(section_data, list):
                        compiled_data = section_data[:]
                    else:
                        compiled_data = section_data
        return compiled_data


