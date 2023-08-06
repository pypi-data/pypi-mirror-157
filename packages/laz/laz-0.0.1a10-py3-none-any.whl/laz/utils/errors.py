class LazError(Exception):
    pass


class LazValueError(LazError, ValueError):
    pass


class LazTypeError(LazError, TypeError):
    pass


class LazRuntimeError(LazError, RuntimeError):
    pass
