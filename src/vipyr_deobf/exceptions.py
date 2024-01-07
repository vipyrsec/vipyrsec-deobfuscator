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
    def __init__(self, deobf_type: str, exception: Exception):
        self.deobf_type = deobf_type
        self.exception = exception
        self.file = None
        super().__init__()

    def __str__(self):
        return f'Deobfuscation of {self.file} with schema <{self.deobf_type}> failed due to exception:'
