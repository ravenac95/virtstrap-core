from virtstrap.registry import CommandRegistry

registry = CommandRegistry()

def register(*args, **kwargs):
    """Shortcut to registry's register method"""
    registry.register(*args, **kwargs)
