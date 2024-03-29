import argparse
import logging
import logging.config
from typing import Callable, NoReturn, TextIO, TypeVar, override

from .deobfuscators.fct import deobf_fct, format_fct
from .deobfuscators.hyperion import deobf_hyperion, format_hyperion
from .deobfuscators.lzmaspam import deobf_lzma_b64, format_lzma_b64
from .deobfuscators.vare import deobf_vare, format_vare
from .exceptions import DeobfuscationFailError, InvalidSchemaError

R = TypeVar('R')

supported_obfuscators: dict[str, tuple[Callable[[TextIO], R], Callable[[R], str]]] = {
    'hyperion': (deobf_hyperion, format_hyperion),
    'lzmaspam': (deobf_lzma_b64, format_lzma_b64),
    'vore': (deobf_vare, format_vare),
    'fct': (deobf_fct, format_fct),
}

alias_dict: dict[str, str] = {
    'vore': 'vare',
    'hyperd': 'hyperion',
    'fct_obfuscate': 'fct',
    'not_pyobfuscate': 'fct',
}


class Color:
    clear = '\x1b[0m'
    red = '\x1b[0;31m'
    green = '\x1b[0;32m'
    yellow = '\x1b[0;33m'
    blue = '\x1b[0;34m'
    white = '\x1b[0;37m'
    bold_red = '\x1b[1;31m'
    bold_green = '\x1b[1;32m'
    bold_yellow = '\x1b[1;33m'
    bold_blue = '\x1b[1;34m'
    bold_white = '\x1b[1;37m'


class NoSoftWarning(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.msg.endswith('(Expected)')


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
    parser.add_argument('-p', '--path', required=True, help='path to obfuscated file')
    parser.add_argument('-t', '--type', help='type of obfuscation used')
    parser.add_argument('-d', '--debug', action='store_true', help='display debug logs (defaults to false)')
    parser.add_argument('-s', '--soft', action='store_true', help='display expected warnings (defaults to false)')
    args = parser.parse_args()

    logger = logging.getLogger('deobf')
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': f'{Color.bold_yellow}[{Color.blue}%(asctime)s{Color.bold_yellow}]'
                          f'{Color.bold_white}:{Color.green}%(levelname)s'
                          f'{Color.bold_white}:{Color.red}%(message)s{Color.clear}'
            }
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
                'filters': [] if args.soft else ['no_soft_warning']
            }
        },
        'filters': {
            'no_soft_warning': {'()': 'src.vipyr_deobf.cli.NoSoftWarning'}
        },
        'loggers': {
            'root': {
                'level': 'DEBUG' if args.debug else 'INFO',
                'handlers': ['stdout']
            }
        }
    }
    logging.config.dictConfig(logging_config)

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
        logger.exception(f'Deobfuscation of {args.path} with schema <{args.type}> failed:')
        for var, data in exc.env_vars.items():
            print(f'{Color.bold_red}{var}{Color.clear}', data, sep='\n', end='\n\n')


if __name__ == '__main__':
    run()
