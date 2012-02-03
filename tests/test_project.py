import fudge
from fudge.inspector import arg
from tests import fixture_path
from tests.tools import *
from virtstrap.project import Project, find_project_dir, ProjectNameProcessor
from virtstrap.options import create_base_parser

def test_initialize_project():
    project = Project()

@fudge.test
def test_project_seeks_project_path():
    from virtstrap.config import VirtstrapConfig
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    base_parser = create_base_parser()
    base_options = base_parser.parse_args(args=[])
    with in_directory(fake_project_sub_directory):
        config = VirtstrapConfig.from_string('')
        project = Project.load(config, base_options)
        assert project.path() == fixture_path('sample_project')
        assert project.name == 'sample_project'

class TestProject(object):
    def setup(self):
        config = fudge.Fake()
        (config.provides('process_section')
                .with_args('project_name', arg.any())
                .returns('projdir'))
        base_parser = create_base_parser()
        options = dict_to_object(dict(virtstrap_dir='/vsdir', 
            project_dir='/projdir'))
        self.project = Project.load(config, options)

    def test_get_project_name(self):
        """Test that the project name is found"""
        project = self.project
        assert project.name == 'projdir'

    def test_project_path(self):
        project = self.project
        assert project.path('a') == '/projdir/a'
        assert project.path('a', 'b') == '/projdir/a/b'

    def test_bin_path(self):
        project = self.project
        assert project.bin_path('a') == '/vsdir/bin/a'
        assert project.bin_path('a', 'b') == '/vsdir/bin/a/b'

    def test_env_path(self):
        project = self.project
        assert project.env_path('a') == '/vsdir/a'
        assert project.env_path('a', 'b') == '/vsdir/a/b'

def test_process_project_name():
    name_processor = ProjectNameProcessor('/projdir/')
    assert 'projdir' == name_processor(None)
    assert 'project_dir' == name_processor('project_dir')
    
def test_find_project_directory_from_lev2():
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    with in_directory(fake_project_sub_directory):
        project_dir = find_project_dir()
        assert project_dir == fixture_path('sample_project')

def test_find_project_directory_from_lev1():
    fake_project_sub_directory = fixture_path('sample_project/lev1')
    with in_directory(fake_project_sub_directory):
        project_dir = find_project_dir()
        assert project_dir == fixture_path('sample_project')

def test_find_project_directory_from_sample_project():
    fake_project_sub_directory = fixture_path('sample_project')
    with in_directory(fake_project_sub_directory):
        project_dir = find_project_dir()
        assert project_dir == fixture_path('sample_project')
