class FlaskOpenIPAException(Exception):
    ...


class MissingRequirementException(FlaskOpenIPAException):
    ...


class MissingSettingException(FlaskOpenIPAException):
    ...


class CantGenerateModelException(FlaskOpenIPAException):
    ...
