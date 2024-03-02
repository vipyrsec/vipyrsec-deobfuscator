import argparse
from typing import Callable, NoReturn, TextIO, TypeVar
import logging

from .deobfuscators.hyperion import format_hyperion, deobf_hyperion
from .deobfuscators.lzmaspam import format_lzma_b64, deobf_lzma_b64
from .deobfuscators.vore import format_vore, deobf_vore
from .deobfuscators.fct import format_fct, deobf_fct
from .exceptions import DeobfuscationFailError, InvalidSchemaError

R = TypeVar('R')

supported_obfuscators: dict[str, tuple[Callable[[TextIO], R], Callable[[R], str]]] = {
    'hyperion': (deobf_hyperion, format_hyperion),
    'lzmaspam': (deobf_lzma_b64, format_lzma_b64),
    'vore': (deobf_vore, format_vore),
    'fct': (deobf_fct, format_fct),
}

alias_dict: dict[str, str] = {
    'vare': 'vore',
    'hyperd': 'hyperion',
    'fct_obfuscate': 'fct',
    'not_pyobfuscate': 'fct',
}


logging.basicConfig(level='DEBUG')
logger = logging.getLogger('deobf')


def run_deobf(file: TextIO, deobf_type: str) -> NoReturn:
    deobf_type = deobf_type.replace('-', '_')
    deobf_type = alias_dict.get(deobf_type, deobf_type)
    if deobf_type not in supported_obfuscators:
        raise InvalidSchemaError

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
        logger.error(f'{args.path} is not a valid path.')
    except InvalidSchemaError:
        logger.error(
            f'Unsupported obfuscation schema.\n'
            f'Supported obfuscation schemes include:\n'
            f'{", ".join(supported_obfuscators)}'
        )
    except DeobfuscationFailError as exc:
        logger.error(f'Deobfuscation of {args.path} with schema <{args.type}> failed:')
        logger.error(exc.msg)


if __name__ == '__main__':
    run()
