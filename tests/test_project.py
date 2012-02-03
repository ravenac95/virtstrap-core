import fudge
from tests import fixture_path
from tests.tools import *
from virtstrap.project import Project, find_project_dir
from virtstrap.options import create_base_parser

def test_initialize_project():
    project = Project()

def test_environment_seeks_path():
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    base_parser = create_base_parser()
    base_options = base_parser.parse_args(args=[])
    with in_directory(fake_project_sub_directory):
        env = Project()
        env.load_options(base_options)
        assert env.project_dir == fixture_path('sample_project')

class TestProject(object):
    def setup(self):
        self.env = Project()
    
    def test_project_path(self):
        options = dict_to_object(dict(project_dir='/projdir'))
        env = self.env
        env.load_options(options)
        assert env.make_project_path('a') == '/projdir/a'
        assert env.make_project_path('a', 'b') == '/projdir/a/b'

    def test_bin_path(self):
        options = dict_to_object(dict(virtstrap_dir='/vsdir', 
            project_dir='/projdir'))
        env = self.env
        env.load_options(options)
        assert env.make_bin_path('test') == '/vsdir/bin/test'

    def test_env_path(self):
        options = dict_to_object(dict(virtstrap_dir='/vsdir', 
            project_dir='/projdir'))
        env = self.env
        env.load_options(options)
        assert env.make_env_path('test') == '/vsdir/test'

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
