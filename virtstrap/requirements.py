from urlparse import urlparse
from virtstrap.exceptions import RequirementsConfigError

class RequirementSet(object):
    @classmethod
    def from_raw_data(cls, raw_data):
        process_raw_requirements(raw_data)
        return cls()

    def set_requirements(self, requirements_list):
        self._requirements_list = requirements_list

    def to_pip_str(self):
        # Process all of the requirements in the 
        # previously set requirements list
        pip_lines = []
        for requirement in self._requirements_list:
            if isinstance(requirement, str):
                # Requirement is a simple string
                pip_lines.append('%s' % requirement)
            elif isinstance(requirement, dict):
                # Requirement is in a dict format
                keys = requirement.keys()
                # It may only have a single key which is the name of the 
                # python module
                if len(keys) != 1:
                    raise RequirementsConfigError('Requirement error. '
                        'Multiple keys encountered for one requirement.')
                requirement_name = keys[0]
                # Get the rest of the data for the requirement
                requirement_data = requirement[requirement_name]
                if isinstance(requirement_data, str):
                    # If the data is a string it is a version specification
                    # or vcs link
                    pip_lines.append('%s%s' % (requirement_name, 
                        requirement_data))
                elif isinstance(requirement_data, list):
                    # If it is a list.
                    # The first element is the version specification or vcs link
                    specification = requirement_data[0]
                    # all other elements are options
                    options = {}
                    for option in requirement_data[1:]:
                        opt_keys = option.keys()
                        option_name = opt_keys[0]
                        options[option_name] = option[option_name]
                    if '+' in specification:
                        prefix = ''
                        if options.get('editable'):
                            prefix = '-e '
                        pip_lines.append('%s%s#egg=%s' % (prefix, 
                            specification, requirement_name))
        return '\n'.join(pip_lines)

def process_raw_requirements(raw_data):
    pass

class Requirement(object):
    def __init__(self, name, version=''):
        self._name = name
        self._version = version

    def to_pip_str(self):
        return '%s%s' % (self._name, self._version)

class URLRequirement(Requirement):
    def __init__(self, name, url):
        self._url = url
        super(URLRequirement, self).__init__(name)
    
    def to_pip_str(self):
        return '%s#egg=%s' % (self._url, self._name)

class VCSRequirement(Requirement):
    def __init__(self, name, url, at=None, editable=False):
        self._url = url
        self._editable = editable
        super(VCSRequirement, self).__init__(name, version=at)

    def to_pip_str(self):
        prefix = ''
        if self._editable:
            prefix = '-e '
        postfix_template = '#egg=%s'
        if self._version:
            postfix_template = '@%s%s' % (self._version, postfix_template)
        postfix = postfix_template % self._name
        return '%s%s%s' % (prefix, self._url, postfix)

class RequirementsProcessor(object):
    """Turns data from configuration into Requirement objects"""
    requirement_types = {
        'basic': Requirement,
        'url': URLRequirement,
        'vcs': VCSRequirement,
    }

    def __init__(self, requirement_types=None):
        self._requirement_types = requirement_types or self.requirement_types

    def to_requirements(self, raw_list):
        requirements = []
        
        for raw_requirement in raw_list:
            if isinstance(raw_requirement, str):
                requirement = self.create_requirement('basic', raw_requirement)
            elif isinstance(raw_requirement, dict):
                requirement = self._handle_requirement_dict(raw_requirement)
            else:
                raise RequirementsConfigError('Unknown requirement format')
            requirements.append(requirement)
        return requirements

    def _handle_requirement_dict(self, raw_requirement):
        """Handle when requirement is in dict form"""
        keys = raw_requirement.keys() 
        # Check that there is one and only one key
        if len(keys) != 1:
            raise RequirementsConfigError('Requirement error. '
                'Multiple keys encountered for one requirement.')
        requirement_name = keys[0]
        requirement_data = raw_requirement[requirement_name]
        if isinstance(requirement_data, str):
            spec_type = self.determine_spec_type(requirement_data)
            return self.create_requirement(spec_type, requirement_name,
                    requirement_data)
        elif isinstance(requirement_data, list):
            spec = requirement_data[0]
            spec_type = self.determine_spec_type(spec)
            options = {}
            for option in requirement_data[1:]:
                opt_keys = option.keys()
                option_name = opt_keys[0]
                options[option_name] = option[option_name]
            return self.create_requirement(spec_type, requirement_name,
                    spec, **options)
        raise RequirementsConfigError('Unknown requirement format')

    def create_requirement(self, requirement_type, *args, **kwargs):
        ReqClass = self._requirement_types.get(requirement_type)
        return ReqClass(*args, **kwargs)

    def determine_spec_type(self, spec):
        """A very naive way to determine the type of requirement"""
        parsed_spec = urlparse(spec)
        scheme = parsed_spec.scheme
        if not scheme:
            return 'basic'
        if '+' in scheme or 'git' in scheme:
            return 'vcs'
        return 'url'
