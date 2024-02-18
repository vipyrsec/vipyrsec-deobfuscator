from typing import Literal


class Error(Exception):
    pass


class InvalidSchemaError(Error):
    def __init__(self, supported: list[str]):
        self.supported = supported

    def __str__(self):
        return (f'Unsupported obfuscation schema.\n'
                f'Supported obfuscation schemes include:\n'
                f'{", ".join(self.supported)}')


class DeobfuscationFailError(Error):
    """
    A generic exception for when deobfuscation fails
    """
    def __init__(
            self,
            msg: str,
            severity: str,
            status: Literal['expected', 'unexpected'],
            exc: Exception | None = None
    ):
        """
        Deobfuscation Failure Innit
        :param msg: A string with details on the cause of the exception
        :param severity: Severity of the exception. Ranges from Low to Critical:
        - Critical: An error occurred and the program cannot proceed.
        - High: An error occurred and the program cannot proceed, but the user can provide input to fix the issue.
        - Mid: A check that should pass has gone off, and program can proceed. Prompt user for confirmation.
        - Low: A check that sometimes passes has gone off, and program can proceed. Warn the user.
        :param status: 'expected' if the program raises this at some point, otherwise 'unexpected'
        :param exc: An optional exception object containing the exception that was raised
        """
        # Note: Prompting the user is fiddly and has not been implemented yet,
        # so currently all of these severities are the same functionally
        self.msg = msg
        self.severity = severity
        self.status = status
        self.exc = exc
        super().__init__()

    def __str__(self):
        # TODO: make better, maybe Enum
        return f"""
\033[0;32mSeverity:\033[0m {self.severity}
\033[0;32mStatus:\033[0m {self.status}
\033[0;32mMessage:\033[0m {self.msg}
"""
