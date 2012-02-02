import subprocess
from functools import wraps

original_subprocess_call = subprocess.call
original_subprocess_popen = subprocess.Popen

def call_proxy(*args, **kwargs):
    """Force call to use the subprocess.PIPE"""
    stdout = kwargs.get('stdout', None)
    if not stdout:
        kwargs['stdout'] = subprocess.PIPE
    return original_subprocess_call(*args, **kwargs)

def popen_proxy(*args, **kwargs):
    """Force Popen to use the subprocess.PIPE"""
    stdout = kwargs.get('stdout', None)
    if not stdout:
        kwargs['stdout'] = subprocess.PIPE
    return original_subprocess_popen(*args, **kwargs)

def hide_subprocess_stdout(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        subprocess.call = call_proxy
        subprocess.Popen = popen_proxy
        return_value = f(*args, **kwargs)
        subprocess.call = original_subprocess_call
        subprocess.Popen = original_subprocess_popen
        return return_value
    return decorated_function
