from contextlib import contextmanager
from jinja2 import Environment, PackageLoader, FileSystemLoader

__all__ = ['environment', 'test_template_enviroment']

_global_environment = None

def environment():
    """Get the global templating environment"""
    global _global_environment
    if not _global_environment:
        _global_environment = Environment(
                loader=PackageLoader('virtstrap', 'templates'))
    return _global_environment

@contextmanager
def temp_template_environment(directory):
    global _global_environment
    original_environment = None
    if _global_environment:
        original_environment = None
    _global_environment = Environment(
            loader=FileSystemLoader(directory))
    try:
        yield
    finally:
        _global_environment = original_environment
