import glob
import importlib.util
import inspect
import logging
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import TypeVar

from vipyr_deobf.exceptions import DeobfLoadingError

R = TypeVar('R')
deobf_path = Path(__file__).parent / 'deobfuscators'

logger = logging.getLogger('deobf')


@dataclass
class Deobfuscator:
    deobf_func: Callable[[str], R]
    format_func: Callable[[R], str]
    scan_func: Callable[[str], bool]
    name: str = field(init=False)
    version: int = field(init=False)

    def __post_init__(self):
        path = Path(inspect.stack()[2].filename)
        rel_path = path.relative_to(deobf_path)
        try:
            module_name, filename = rel_path.parts
        except ValueError:
            raise DeobfLoadingError('Deobfuscator was not initialized in a deobf module: see repo README')
        obf_name = normalize_deobf_name(module_name)
        res = parse_deobf_file_name(filename)
        if not res:
            raise DeobfLoadingError('Filename does not match module name: see repo README')
        name, version = res
        if name != obf_name:
            raise DeobfLoadingError('Filename does not match module name: see repo README')
        self.name = name
        self.version = version

    def deobf(self, obf: str) -> R:
        return self.deobf_func(obf)

    def format_results(self, res: R) -> str:
        return self.format_func(res)

    def scan(self, obf: R) -> bool:
        return self.scan_func(obf)


DEOBFS: dict[str, dict[int, Deobfuscator]] = {}


def normalize_deobf_name(name: str) -> str:
    return name.lower().replace(' ', '')


def parse_deobf_file_name(filename: str) -> tuple[str, int] | None:
    res = re.match(fr'([a-zA-Z]+)(?:_v(\d+))?\.py$', filename)
    if not res:
        return None
    return res.group(1), int(res.group(2) or 1)


def register(deobf: Deobfuscator) -> None:
    deobf_versions = DEOBFS.setdefault(deobf.name, {})
    if deobf.version in deobf_versions:
        raise DeobfLoadingError(f'Version {deobf.version} of {deobf.name} has already been loaded')
    deobf_versions[deobf.version] = deobf


alias_dict = {
    'vore': 'vare',
    'hyperd': 'hyperion',
    'fct_obfuscate': 'fct',
    'not_pyobfuscate': 'fct',
}


@cache
def get_available_deobfs() -> dict[str, dict[int, Path]]:
    available_deobfs = {}
    for deobf_dir in deobf_path.iterdir():
        deobf_name = normalize_deobf_name(deobf_dir.name)
        available_deobfs[deobf_name] = {
            res[1]: file
            for file in deobf_dir.glob(f'{glob.escape(deobf_name)}*.py')
            if (res := parse_deobf_file_name(file.name)) and res[0] == deobf_name
        }
    return available_deobfs


def load_deobfs(opt_str: str) -> None:
    available_deobfs = get_available_deobfs()
    for deobf_type in opt_str.split(','):
        res = re.match(r'([a-zA-Z]+)(?:_(\d+))?$', deobf_type)
        if not res:
            raise DeobfLoadingError(f'{deobf_type} is an invalid schema option')
        name = normalize_deobf_name(res.group(1))
        name = alias_dict.get(name, name)
        version = int(res.group(2) or 1)
        if name not in available_deobfs:
            raise DeobfLoadingError(f'{name} is not the name of a deobfuscator')
        elif version not in available_deobfs[name]:
            raise DeobfLoadingError(f'Version {version} of {name} does not exist')
        spec = importlib.util.spec_from_file_location('bobin', available_deobfs[name][version])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def load_all_deobfs() -> None:
    available_deobfs = get_available_deobfs()
    for versions in available_deobfs.values():
        for deobf in versions.values():
            logger.info(f'Loading {deobf.stem}')
            spec = importlib.util.spec_from_file_location('bobin', deobf)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logger.info(f'Finished loading {deobf.stem}')


def iter_deobfs() -> Iterator[Deobfuscator]:
    return (
        deobf
        for versions in DEOBFS.values()
        for deobf in versions.values()
    )
