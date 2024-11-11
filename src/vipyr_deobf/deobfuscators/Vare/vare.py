"""
Deobfuscator for vare
https://github.com/saintdaddy/Vare-Obfuscator/blob/main/Vare.py
It says __VareObfuscator__ = '' at the top
"""

import ast
import base64
import logging
import re
import zlib

from cryptography.fernet import Fernet

from build.lib.vipyr_deobf.exceptions import DeobfuscationFailError
from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.deobf_utils import WEBHOOK_REGEX

logger = logging.getLogger('deobf')


def deobf_layer(code: str) -> str:
    """
    Extracts the entire source code from code layer
    """
    key = ast.literal_eval(re.search(r'__mikey__\s*=\s*(([\'"]).+\2);mydata', code).group(1))
    data = ast.literal_eval(re.search(r'mydata\s*=\s*(([\'"]).+\2)', code).group(1))
    fernet = Fernet(base64.b64decode(key))
    marshalled = zlib.decompress(base64.b32decode(base64.b64decode(
        base64.b64decode(base64.b64decode(base64.b32decode(
            base64.b64decode(fernet.decrypt(bytes.fromhex(data)))
        )))[::-1]
    )))
    try:
        return str_unmarshal(marshalled)
    except DeobfuscationFailError:
        return f'{marshalled}'


def deobf(code: str) -> str:
    i = 0
    while scan(code):
        logger.info(f'Deobfuscating layer {i}')
        code = deobf_layer(code)
        i += 1
    logger.info(f'Finished deobfuscating at layer {i}')
    return code


def str_unmarshal(marshalled: bytes) -> str:
    """
    Unmarshals a marshalled string, which is what vare is
    """
    total_length = len(marshalled)
    payload_length = total_length - 5
    if not marshalled.startswith(b's'):
        logger.error('Marshalled object was not a string')
        raise DeobfuscationFailError()
    expected_length = int.from_bytes(marshalled[1:5], 'little')
    if expected_length != payload_length:
        logger.error('Marshalled object length does not match expected length')
        raise DeobfuscationFailError()
    return marshalled[5:].decode('utf-8')


def format_results(result: str) -> str:
    return result + '\n\n' + '\n'.join(re.findall(WEBHOOK_REGEX, result))


VARE_NAME_REGEX = re.compile(r'__VareObfuscator__')
SAINT_REGEX = re.compile(r'def saint\d+\(\):')
MIKEY_REGEX = re.compile(r'__mikey__')


def scan(code: str):
    return any(
        pattern.search(code)
        for pattern in (
            VARE_NAME_REGEX,
            SAINT_REGEX,
            MIKEY_REGEX,
        )
    )


vare_deobf = Deobfuscator(deobf, format_results, scan)
register(vare_deobf)
