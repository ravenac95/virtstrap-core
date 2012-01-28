class RequirementsProcessor(object):
    @classmethod
    def from_list(cls, requirements_list):
        return cls()

    def set_requirements(self, requirements_list):
        self._requirements_list = requirements_list

    def create_requirements_file(self, file=None):
        # FIXME Fake implementation
        import textwrap
        file.write(textwrap.dedent("""
            ipython
            werkzeug==0.8
            requests
            -e git+https://github.com/mitsuhiko/jinja2.git#egg=jinja2
        """))
