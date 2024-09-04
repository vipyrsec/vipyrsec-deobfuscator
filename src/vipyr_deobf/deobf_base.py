from typing import Protocol, TextIO
from abc import abstractmethod
from exceptions import DeobfuscationFailError
import re


class Deobfuscator(Protocol):
    name: str
    version: int
    file: TextIO
    results: {}

    def __init__(self, file: TextIO):
        self.file = file
        self.results = {}

    def scan(self) -> bool:
        try:
            self.deobf()
        except DeobfuscationFailError:
            return False
        return True

    @abstractmethod
    def deobf(self) -> None:
        ...

    @abstractmethod
    def write_results(self, output: TextIO) -> None:
        ...


_DEOBFS: dict[str, dict[int, type[Deobfuscator]]] = {}


def normalize_deobf_name(name: str) -> str:
    return name.lower().replace(' ', '')


def register(deobf: type[Deobfuscator]) -> type[Deobfuscator]:
    package, _, name = deobf.__module__.rpartition('.')
    if re.search(r'\.v(\d+)$', package):
        package, _, version_str = package.rpartition('.')
        version = int(version_str[2:])
    else:
        version = 1
    deobf_versions = _DEOBFS.setdefault(package, {})
    deobf_versions[version] = deobf
    return deobf

