# PYTHON_ARGCOMPLETE_OK
import argparse
import importlib.util
import logging
from typing import Any

from vipyr_deobf.deobf_base import (
    Deobfuscator,
    get_available_deobfs,
    iter_deobfs,
    load_all_deobfs,
    load_deobfs,
)
from vipyr_deobf.exceptions import DeobfuscationFailError
from vipyr_deobf.utils import Color, setup_logging


def get_parser():
    parser = argparse.ArgumentParser(
        prog='Vipyr Deobfuscator',
        description='Deobfuscates obfuscated scripts',
        epilog='Available deobfuscators:\n'
        + '\n'.join(
            f'  - {deobf_name} v{version}'
            for deobf_name, versions in get_available_deobfs().items()
            for version in versions
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('path', help='path to obfuscated file')
    parser.add_argument(
        '-t',
        '--type',
        default='auto',
        type=str,
        help='type of obfuscation used, see help for options (defaults to auto)',
    )
    parser.add_argument(
        '-o', '--output', help='file to output deobf result to (defaults to stdout)'
    )
    parser.add_argument(
        '-s',
        '--skip-scan',
        action='store_true',
        help='skip scanning phase to identify schema',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='display debug logs')
    parser.add_argument(
        '--show-expected', action='store_true', help='display expected warnings'
    )
    return parser


def run():
    parser = get_parser()
    if importlib.util.find_spec('argcomplete') is not None:
        import argcomplete  # type: ignore

        argcomplete.autocomplete(parser)  # type: ignore

    args = parser.parse_args()

    logger = logging.getLogger('deobf')
    setup_logging(args)
    logger.info('Logging setup finished')

    logger.info(f'Opening file at {args.path}')
    try:
        with open(args.path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        logger.error(f'{args.path} is not a valid path.')
        return
    logger.info('Data successfully read from file')

    logger.info('Loading deobfuscators...')
    if args.type == 'auto':
        load_all_deobfs()
    else:
        load_deobfs(args.type)

    deobfs: list[Deobfuscator[Any]]
    if args.skip_scan:
        deobfs = [*iter_deobfs()]
    else:
        logger.info('Running scanners...')
        deobfs = []
        for deobf in iter_deobfs():
            logger.info(f'Scanning with schema {deobf.name}v{deobf.version}')
            if deobf.scan(data):
                logger.info('Scan succeeded, adding to schema list')
                deobfs.append(deobf)
            else:
                logger.info('Scan failed, skipping')
    logger.info(f'Schema list: {", ".join([deobf.name for deobf in deobfs])}')

    for deobf in deobfs:
        try:
            logger.info(f'Running deobf of {args.path} with schema {deobf.name}')
            results = deobf.deobf(data)
            output = deobf.format_results(results)
        except DeobfuscationFailError as exc:
            logger.exception(
                f'Deobfuscation of {args.path} with schema {deobf.name} failed:'
            )
            for var, data in exc.env_vars.items():
                print(f'{Color.bold_red}{var}{Color.clear}', data, sep='\n', end='\n\n')
        else:
            if args.output is None:
                print(output)
            else:
                logger.info(f'Writing results of deobf to file {args.output}')
                with open(args.output, 'w') as file:
                    file.write(output)
            break
