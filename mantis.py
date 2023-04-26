import argparse
import traceback
from typing import Callable, NoReturn, TextIO, TypeVar

from exceptions import DeobfuscationFailError, InvalidSchemaError
from hyperion import format_hyperion, hyperion_deobf
from lzmaspam import format_lzma_b64, lzma_b64_deobf
from vore import format_vore, vore_deobf

R = TypeVar('R')

supported_obfuscators: dict[str, tuple[Callable[[TextIO], R], Callable[[R], str]]] = {
    'hyperion': (hyperion_deobf, format_hyperion),
    'lzmaspam': (lzma_b64_deobf, format_lzma_b64),
    'vore': (vore_deobf, format_vore),
}

alias_dict: dict[str, str] = {
    'vare': 'vore',
}


def run_deobf(file: TextIO, deobf_type: str) -> NoReturn:
    deobf_type = alias_dict.get(deobf_type, deobf_type)
    if deobf_type not in supported_obfuscators:
        raise InvalidSchemaError([*supported_obfuscators])

    deobf_func, format_func = supported_obfuscators[deobf_type]
    try:
        results = deobf_func(file)
    except Exception as e:
        raise DeobfuscationFailError(
            deobf_type=deobf_type,
            exception=e
        )
    print(format_func(results))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Mantis Deobfuscator',
        description='Deobfuscates obfuscated scripts'
    )
    parser.add_argument('-p', '--path')
    parser.add_argument('-t', '--type')
    args = parser.parse_args()
    try:
        with open(args.path, 'r') as file:
            run_deobf(file, args.type)
    except FileNotFoundError:
        print(f'{args.path} is not a valid path.')
    except InvalidSchemaError as e:
        print(e)
    except DeobfuscationFailError as e:
        e.file = args.path
        print(e)
        print('\033[0;32m', *traceback.format_exception(e.exception))

