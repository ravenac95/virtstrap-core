from cStringIO import StringIO
import textwrap
import fudge
from virtstrap.requirements import RequirementsProcessor

TEST_REQUIREMENTS_YML = """
requirements:
  - ipython
  - jinja2:
    - https://github.com/mitsuhiko/jinja2.git
    - editable: true
  - werkzeug: '==0.8'
  - requests: '>=0.8'
"""

def test_initialize_processor():
    processor = RequirementsProcessor()

def test_initialize_from_data():
    processor = RequirementsProcessor.from_list([])
    assert isinstance(processor, RequirementsProcessor)

class TestRequirementsProcessor(object):
    """RequirementsProcessor test without mocks"""

    def setup(self):
        self.processor = RequirementsProcessor()

    def test_create_requirements_file(self):
        # Define a requirements list
        requirements_list = [
            'ipython',
            {'werkzeug': '==0.8'},
            {'requests': '>=0.8'},
            {'jinja2': [
                'git+https://github.com/mitsuhiko/jinja2.git',
                {'editable': True},
            ]}
        ]
        # Define the expected created file
        expected_file = textwrap.dedent("""
            ipython
            werkzeug==0.8
            requests
            -e git+https://github.com/mitsuhiko/jinja2.git#egg=jinja2
        """)
        self.processor.set_requirements(requirements_list)
        
        fake_file = StringIO()

        self.processor.create_requirements_file(file=fake_file)

        fake_file_value = fake_file.getvalue()
        stripped_fake_file = fake_file_value.strip()
        stripped_expected_file = expected_file.strip()

        assert stripped_fake_file == stripped_expected_file

class TestRequirementsProcessorAlone(object):
    """RequirementsProcessor test using mocks"""
    def setup(self):
        self.processor = RequirementsProcessor()

