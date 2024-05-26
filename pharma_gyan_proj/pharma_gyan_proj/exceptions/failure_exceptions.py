class BadRequestException(Exception):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.error = kwargs.get("error")
        self.reason = kwargs.get("reason")

class InvalidRidException(BadRequestException):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.error = kwargs.get("error")
        self.reason = kwargs.get("reason")

class UnauthorizedException(BadRequestException):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.error = kwargs.get("error")
        self.reason = kwargs.get("reason")

class MySQLException(Exception): 
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MethodPermissionValidationException(Exception):
    pass


class ValidationFailedException(Exception):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.error = kwargs.get("error")
        self.reason = kwargs.get("reason")
        self.data = kwargs.get("data")


class NotFoundException(Exception):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.error = kwargs.get("error")
        self.reason = kwargs.get("reason")


class InternalServerError(Exception):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.error = kwargs.get("error")
        self.reason = kwargs.get("reason")


class OtpRequiredException(Exception):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.data = kwargs.get("data")


class CampaignAcknowledgeRequiredException(Exception):
    def __init__(self, **kwargs):
        self.method_name = kwargs.get("method_name")
        self.data = kwargs.get("data")


class QueryTimeoutException(Exception):
    pass


class EmptySegmentException(Exception):
    pass