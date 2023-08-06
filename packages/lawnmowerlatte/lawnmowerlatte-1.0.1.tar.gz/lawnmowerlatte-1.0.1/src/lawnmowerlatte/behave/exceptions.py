class LexicalAnalzyerException(Exception):
    pass


class LexicalAnalzyerTokenizationError(LexicalAnalzyerException):
    pass


class LexicalAnalzyerPathError(LexicalAnalzyerException):
    pass


class LexicalAnalzyerDataError(LexicalAnalzyerException):
    pass


class LexicalAnalzyerParameterError(LexicalAnalzyerException):
    pass


class TimeoutError(Exception):
    pass
