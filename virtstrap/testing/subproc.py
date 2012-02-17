import subprocess
from fudge.patcher import patch_object
from functools import wraps
from virtstrap import utils

original_subprocess_call = subprocess.call
original_subprocess_popen = subprocess.Popen
original_call_subprocess = utils.call_subprocess

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

def call_subprocess_proxy(*args, **kwargs):
    kwargs['show_stdout'] = False
    raise Exception()
    return original_call_subprocess(*args, **kwargs)

def hide_subprocess_stdout(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        call_patch = patch_object('subprocess', 'call', call_proxy)
        popen_patch = patch_object('subprocess', 'Popen', popen_proxy)
        call_sub_patch = patch_object('virtstrap.utils', 'call_subprocess', call_subprocess_proxy)
        return_value = f(*args, **kwargs)
        call_patch.restore()
        popen_patch.restore()
        call_sub_patch.restore()
        return return_value
    return decorated_function

def hide_subprocess_stdout(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        call_patch = patch_object('subprocess', 'call', call_proxy)
        popen_patch = patch_object('subprocess', 'Popen', popen_proxy)
        call_sub_patch = patch_object('virtstrap.utils', 'call_subprocess', call_subprocess_proxy)
        return_value = f(*args, **kwargs)
        call_patch.restore()
        popen_patch.restore()
        call_sub_patch.restore()
        return return_value
    return decorated_function
