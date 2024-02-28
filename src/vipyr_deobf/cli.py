import argparse
from typing import Callable, NoReturn, TextIO, TypeVar

from .deobfuscators.hyperion import format_hyperion, deobf_hyperion
from .deobfuscators.lzmaspam import format_lzma_b64, deobf_lzma_b64
from .deobfuscators.vore import format_vore, deobf_vore
from .deobfuscators.not_pyobfuscate import format_not_pyobfuscate, deobf_not_pyobfuscate
from .exceptions import DeobfuscationFailError, InvalidSchemaError

R = TypeVar('R')

supported_obfuscators: dict[str, tuple[Callable[[TextIO], R], Callable[[R], str]]] = {
    'hyperion': (deobf_hyperion, format_hyperion),
    'lzmaspam': (deobf_lzma_b64, format_lzma_b64),
    'vore': (deobf_vore, format_vore),
    'not_pyobfuscate': (deobf_not_pyobfuscate, format_not_pyobfuscate),
}

alias_dict: dict[str, str] = {
    'vare': 'vore',
    'hyperd': 'hyperion',
    'fct-obfuscate': 'not_pyobfuscate',
}


def run_deobf(file: TextIO, deobf_type: str) -> NoReturn:
    deobf_type = alias_dict.get(deobf_type, deobf_type)
    if deobf_type not in supported_obfuscators:
        raise InvalidSchemaError([*supported_obfuscators])

    deobf_func, format_func = supported_obfuscators[deobf_type]
    results = deobf_func(file)
    print(format_func(results))


def run():
    parser = argparse.ArgumentParser(
        prog='Vipyr Deobfuscator',
        description='Deobfuscates obfuscated scripts',
    )
    parser.add_argument('-p', '--path')
    parser.add_argument('-t', '--type')
    args = parser.parse_args()
    try:
        with open(args.path, 'r') as file:
            run_deobf(file, args.type)
    except FileNotFoundError:
        print(f'{args.path} is not a valid path.')
    except InvalidSchemaError as exc:
        print(exc)
    except DeobfuscationFailError as exc:
        print(f'Deobfuscation of {args.path} with schema <{args.type}> failed:')
        print(exc)


if __name__ == '__main__':
    run()
