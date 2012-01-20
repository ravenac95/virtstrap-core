import os

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

def fixture_path(file_path):
    return os.path.join(TEST_DIR, "fixture", file_path)
