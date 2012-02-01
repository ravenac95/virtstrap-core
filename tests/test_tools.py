import os
import urllib2
from tests.tools import *

def test_temp_directory():
    """Test a temp directory"""
    with in_temp_directory() as temp_directory:
        assert os.getcwd() == temp_directory
    assert os.path.exists(temp_directory) == False

def test_temp_directory_write_file():
    """Test temp directory and create file there"""
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

def test_fake_pypi():
    packages_directory = 'tests/fixtures/packages'
    with temp_pip_index(packages_directory) as index_url:
        urllib2.urlopen(index_url)
