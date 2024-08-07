# PYTHON_ARGCOMPLETE_OK
import argparse
import logging
import logging.config
import importlib.util
from typing import Callable, TypeVar

from .deobfuscators.blankobf2 import deobf_blankobf2, format_blankobf2
from .deobfuscators.fct import deobf_fct, format_fct
from .deobfuscators.hyperion import deobf_hyperion, format_hyperion
from .deobfuscators.lzmaspam import deobf_lzma_b64, format_lzma_b64
from .deobfuscators.pyobfuscate import deobf_pyobfuscate, format_pyobfuscate
from .deobfuscators.vare import deobf_vare, format_vare
from .exceptions import DeobfuscationFailError
from .scanners.blankobf2_scan import scan_blankobf2
from .scanners.fct_scan import scan_fct
from .scanners.hyperion_scan import scan_hyperion
from .scanners.lzmaspam_scan import scan_lzma
from .scanners.pyobfuscate_scan import scan_pyobfuscate
from .scanners.vare_scan import scan_vare

R = TypeVar('R')

supported_obfuscators: dict[str, tuple[Callable[[str], R], Callable[[R], str]]] = {
    'hyperion': (deobf_hyperion, format_hyperion),
    'lzmaspam': (deobf_lzma_b64, format_lzma_b64),
    'vare': (deobf_vare, format_vare),
    'fct': (deobf_fct, format_fct),
    'blankobf2': (deobf_blankobf2, format_blankobf2),
    'pyobfuscate': (deobf_pyobfuscate, format_pyobfuscate),
}

scanners: dict[str, Callable[[str], bool]] = {
    'hyperion': scan_hyperion,
    'lzmaspam': scan_lzma,
    'vare': scan_vare,
    'fct': scan_fct,
    'blankobf2': scan_blankobf2,
    'pyobfuscate': scan_pyobfuscate,
}

alias_dict: dict[str, str] = {
    'vore': 'vare',
    'hyperd': 'hyperion',
    'fct_obfuscate': 'fct',
    'not_pyobfuscate': 'fct',
    'blankobfv2': 'blankobf2',
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
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.msg.endswith('(Expected)')


def run_deobf(code: str, deobf_type: str) -> str:
    deobf_func, format_func = supported_obfuscators[deobf_type]
    results = deobf_func(code)
    return format_func(*results) if isinstance(results, tuple) else format_func(results)


def setup_logging(args: argparse.Namespace):
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
            'no_soft_warning': {'()': 'vipyr_deobf.cli.NoSoftWarning'}
        },
        'loggers': {
            'root': {
                'level': 'DEBUG' if args.debug else 'INFO',
                'handlers': ['stdout']
            }
        }
    }
    logging.config.dictConfig(logging_config)


def run():
    parser = argparse.ArgumentParser(
        prog='Vipyr Deobfuscator',
        description='Deobfuscates obfuscated scripts',
    )
    parser.add_argument('path', help='path to obfuscated file')
    parser.add_argument('-t', '--type', default='auto', type=str,
                        choices=list(supported_obfuscators.keys()).append('auto'),
                        help='type of obfuscation used (defaults to auto)')
    parser.add_argument('-o', '--output', help='file to output deobf result to, defaults to stdout')
    parser.add_argument('-d', '--debug', action='store_true', help='display debug logs (defaults to false)')
    parser.add_argument('-s', '--soft', action='store_true', help='display expected warnings (defaults to false)')
    if importlib.util.find_spec('argcomplete') is not None:
        import argcomplete
        argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logger = logging.getLogger('deobf')
    setup_logging(args)

    try:
        with open(args.path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        logger.error(f'{args.path} is not a valid path.')
        return

    schemas = []
    if args.type == 'auto':
        logger.info('Scanning file to identify schema')
        for schema, scanner in scanners.items():
            if scanner(data):
                schemas.append(schema)
        if not schemas:
            logger.error('Could not identify obfuscation schema')
            return
        logger.info(f'Schemas matched: {", ".join(schemas)}')
    else:
        deobf_type = args.type.replace('-', '_')
        deobf_type = alias_dict.get(deobf_type, deobf_type)
        if deobf_type not in supported_obfuscators:
            logger.error(
                f'Unsupported obfuscation schema.\n'
                f'Supported obfuscation schemes include:\n'
                f'{", ".join(supported_obfuscators)}'
            )
            return
        schemas.append(deobf_type)

    for schema in schemas:
        try:
            logger.info(f'Running deobf of {args.path} with schema <{schema}>')
            output = run_deobf(data, schema)
        except DeobfuscationFailError as exc:
            logger.exception(f'Deobfuscation of {args.path} with schema <{schema}> failed:')
            for var, data in exc.env_vars.items():
                print(f'{Color.bold_red}{var}{Color.clear}', data, sep='\n', end='\n\n')
        else:
            if args.output is None:
                print(output)
            else:
                logger.info(f'Writing results of deobf to file {args.output}')
                with open(args.output, 'w') as file:
                    file.write(output)


if __name__ == '__main__':
    run()
