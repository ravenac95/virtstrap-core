from virtstrap.registry import CommandRegistry
# Conveniently provide Command and ProjectCommand
from virtstrap.basecommand import * 

registry = CommandRegistry()

def register(*args, **kwargs):
    """Shortcut to registry's register method"""
    registry.register(*args, **kwargs)

def run(*args, **kwargs):
    """Shortcut to the registry's run method"""
    registry.run(*args, **kwargs)
