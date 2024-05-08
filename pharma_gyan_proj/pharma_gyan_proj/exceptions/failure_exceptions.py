class BadRequestException(Exception):
    pass

class InvalidRidException(BadRequestException):
    pass

class UnauthorizedException(BadRequestException):
    pass

class MySQLException(Exception): 
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)