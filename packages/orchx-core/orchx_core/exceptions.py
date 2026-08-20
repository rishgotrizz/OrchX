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


class ProviderError(OrchXException):
    """Base exception for provider and LLM routing runtime errors."""
    def __init__(self, message: str, error_code: str):
        self.error_code = error_code
        super().__init__(message)


class NoProviderConfiguredError(ValueError, ProviderError):
    def __init__(self, message: str = "No AI providers are configured yet."):
        ValueError.__init__(self, message)
        ProviderError.__init__(self, message, "NO_PROVIDER_CONFIGURED")


class ProviderNotConfiguredError(ValueError, ProviderError):
    def __init__(self, provider: str):
        msg = f"Provider {provider} is not configured."
        ValueError.__init__(self, msg)
        ProviderError.__init__(self, msg, "PROVIDER_NOT_CONFIGURED")


class ProviderAuthFailedError(ValueError, ProviderError):
    def __init__(self, provider: str, message: str = "Provider authentication failed."):
        ValueError.__init__(self, message)
        ProviderError.__init__(self, message, "PROVIDER_AUTH_FAILED")


class ProviderUnavailableError(ConnectionError, ProviderError):
    def __init__(self, provider: str, message: str = "Provider is temporarily unavailable."):
        ConnectionError.__init__(self, message)
        ProviderError.__init__(self, message, "PROVIDER_UNAVAILABLE")


class ProviderTimeoutError(TimeoutError, ProviderError):
    def __init__(self, provider: str, message: str = "Provider request timed out."):
        TimeoutError.__init__(self, message)
        ProviderError.__init__(self, message, "PROVIDER_TIMEOUT")


class ProviderRequestFailedError(ConnectionError, ProviderError):
    def __init__(self, provider: str, message: str = "Provider request failed."):
        ConnectionError.__init__(self, message)
        ProviderError.__init__(self, message, "PROVIDER_REQUEST_FAILED")


class InvalidProviderConfigurationError(ValueError, ProviderError):
    def __init__(self, message: str = "Invalid provider configuration."):
        ValueError.__init__(self, message)
        ProviderError.__init__(self, message, "INVALID_PROVIDER_CONFIGURATION")
