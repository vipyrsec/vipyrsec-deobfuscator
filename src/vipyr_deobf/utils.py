import argparse
import logging
import logging.config


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


def setup_logging(args: argparse.Namespace | None = None):
    show_expected = True if args is None else args.show_expected
    debug = False if args is None else args.show_expected
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
                'filters': [] if show_expected else ['no_soft_warning']
            }
        },
        'filters': {
            'no_soft_warning': {'()': 'vipyr_deobf.utils.NoSoftWarning'}
        },
        'loggers': {
            'root': {
                'level': 'DEBUG' if debug else 'INFO',
                'handlers': ['stdout']
            }
        }
    }
    logging.config.dictConfig(logging_config)
