import tempfile
import os
import shutil
from contextlib import contextmanager

@contextmanager
def in_temp_directory():
    """Context manager for a changing CWD to a temporary directory
    
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

@contextmanager
def temp_directory():
    """Context manager for a temporary directory

    Creates a temporary directory and deletes once done
    """
    # Create temp directory
    temp_directory = tempfile.mkdtemp()
    # Ensure that we have the real path not some symlink
    temp_directory = os.path.realpath(temp_directory)
    # yield control to the context
    try:
        # if any errors occur it will still be deleted
        yield temp_directory
    finally:
        # Delete temp directory
        shutil.rmtree(temp_directory)

@contextmanager
def in_directory(directory):
    """Context manager for changing CWD to a directory

    Don't use this if you plan on writing files to the directory.
    This does not delete anything. It is purely to change the CWD
    """
    # Save current state
    original_directory = os.getcwd()
    # Change the directory to the new cwd
    os.chdir(directory)
    try:
        yield temp_directory
    finally:
        # Return all changed settings to original directory
        os.chdir(original_directory)

