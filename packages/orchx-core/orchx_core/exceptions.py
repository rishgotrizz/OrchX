class OrchXException(Exception):
    """Base exception for all OrchX errors."""
    pass


class PluginLoadError(OrchXException):
    """Raised when a plugin fails to parse, validate, or instantiate."""
    pass


class PluginLifecycleError(OrchXException):
    """Raised when a lifecycle hook fails to execute correctly."""
    pass


class CapabilityViolationError(OrchXException):
    """Raised when a plugin attempts to invoke an unauthorized tool action."""
    pass


class ConfigurationError(OrchXException):
    """Raised when configuration values are missing or invalid."""
    pass
