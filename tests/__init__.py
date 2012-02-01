import os
import sys

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TESTS_DIR, '..'))
FIXTURES_DIR = os.path.abspath(os.path.join(TESTS_DIR, 'fixtures'))

sys.path.insert(0, PROJECT_DIR)

def fixture_path(file_path):
    return os.path.join(FIXTURES_DIR, file_path)

def open_fixture_file(filename, mode='r'):
    file_path = os.path.join(FIXTURES_DIR, filename)
    fixture = open(file_path, mode)
    return fixture
