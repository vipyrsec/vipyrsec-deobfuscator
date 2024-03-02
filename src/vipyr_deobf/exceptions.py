import inspect
from typing import Any


class Error(Exception):
    pass


class InvalidSchemaError(Error):
    pass


class DeobfuscationFailError(Error):
    """
    A generic exception for when deobfuscation fails
    """
    def __init__(self, msg: str, exc: Exception | None = None, data: dict[str, Any] = None):
        """
        Deobfuscation Failure
        :param msg: A string with details on the cause of the exception
        :param exc: An optional exception object containing the exception that was raised
        """
        self.msg = msg
        self.exc = exc
        self.data = data
        super().__init__()
