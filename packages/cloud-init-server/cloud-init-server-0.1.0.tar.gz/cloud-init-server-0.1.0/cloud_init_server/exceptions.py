

class ServiceConfigError(Exception):
    """Base class for other exceptions"""
    pass

class MissingConfigProperty(ServiceConfigError):
    """Base class for other exceptions"""
    pass