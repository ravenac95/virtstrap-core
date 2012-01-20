import tempfile
import os
import shutil
from contextlib import contextmanager

@contextmanager
def in_temp_directory():
    """Context manager for a temporary directory
    
    This is a tool to create a temporary directory and changes directory
    to the temporary directory.
    """
    # Save current state
    current_directory = os.getcwd()
    # Create temp directory
    temp_directory = tempfile.mkdtemp()
    # Ensure that we have the real path not some symlink
    temp_directory = os.path.realpath(temp_directory)
    # Change directory to temp directory
    os.chdir(temp_directory)
    # yield control to the context
    try:
        # if any errors occur it will still be deleted
        yield temp_directory
    finally:
        # Return all changed settings to normal original
        os.chdir(current_directory)
        # Delete temp directory
        shutil.rmtree(temp_directory)
