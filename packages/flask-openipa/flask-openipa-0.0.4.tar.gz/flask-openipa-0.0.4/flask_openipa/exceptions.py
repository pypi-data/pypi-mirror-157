"""This module defines exceptions that might be raised by FlaskOpenIPA extension."""

class FlaskOpenIPAException(Exception):
    """Base exception for FlaskOpenIPA exceptions
    
    Arguments:
        message: A string describing context of the exception
    """


class MissingRequirementException(FlaskOpenIPAException):
    """Exception raised when a dependency for a plugin is not satisfied
    
    Arguments:
        message: A string describing context of the exception
    """


class MissingSettingException(FlaskOpenIPAException):
    """Exception raised when a required setting is not set in Flask config
    
    Arguments:
        message: A string describing context of the exception
    """


class CantGenerateModelException(FlaskOpenIPAException):
    """Exception raised when a plugin failed to generate an openapi model

    When this exception is raised in SchemaBuilder, the next plugin is called.
    
    Arguments:
        message: A string describing context of the exception
    """
