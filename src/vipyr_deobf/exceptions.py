class Error(Exception):
    pass


class InvalidSchemaError(Error):
    pass


class DeobfuscationFailError(Error):
    """
    A generic exception for when deobfuscation fails
    """
    def __init__(self, **env_vars):
        """
        Deobfuscation Failure
        :param env_vars: Relevant environment variables for debugging
        """
        self.env_vars = env_vars
        super().__init__()
