import os
import urllib2
from nose.plugins.attrib import attr
from tests.tools import *
from tests import fixture_path

def test_in_directory():
    """Test change CWD to a specific directory"""
    basic_project_dir = fixture_path('sample_project')
    with in_directory(basic_project_dir):
        assert basic_project_dir == os.path.abspath('.')
    assert basic_project_dir != os.path.abspath('.')

def test_temp_directory():
    """Test temp directory correctly deletes"""
    with temp_directory() as temp_dir:
        pass
    assert os.path.exists(temp_dir) == False

def test_in_temp_directory():
    """Test CWD to temp directory"""
    with in_temp_directory() as temp_directory:
        assert os.getcwd() == temp_directory
    assert os.path.exists(temp_directory) == False

def test_in_temp_directory_write_file():
    """Test CWD to temp directory and create file there"""
    with in_temp_directory() as temp_directory:
        # Create a test file in the directory
        test_filename = "test_file.txt"
        test_file = open(test_filename, "w")
        # Put some random data in it
        random_data = random_string(15)
        test_file.write(random_data)
        test_file.close()
        # Attempt to open the file using the full path to the temp directory 
        test_file_path = os.path.join(temp_directory, test_filename)
        # Verify contents
        verify_file = open(test_file_path)
        verify_data = verify_file.read()
        assert random_data == verify_data

@attr('slow')
def test_fake_pypi():
    packages_directory = 'tests/fixture/packages'
    with temp_pip_index(packages_directory) as index_url:
        urllib2.urlopen(index_url)

@hide_subprocess_stdout
def test_subprocess_popen_proxy():
    import subprocess
    process = subprocess.Popen(['echo', 'hello'])
    process.wait()
    process_stdout = getattr(process, 'stdout', None)
    output = process_stdout.read()
    assert process_stdout is not None
    assert output == 'hello\n'
    
def test_dict_to_object():
    obj = dict_to_object(dict(a=1,b=2))
    assert obj.a == 1
    assert obj.b == 2
