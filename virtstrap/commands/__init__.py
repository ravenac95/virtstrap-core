"""
virtstrap.commands
------------------

This is the main frontend for the command registry and for the Command 
classes.
"""

from virtstrap.registry import CommandRegistry
# Conveniently provide Command and ProjectCommand
from virtstrap.basecommand import * 

# Global Command Registry
registry = CommandRegistry()

def register(*args, **kwargs):
    """Shortcut to registry's register method"""
    registry.register(*args, **kwargs)

def run(*args, **kwargs):
    """Shortcut to the registry's run method"""
    registry.run(*args, **kwargs)
