"""
Deobfuscator for vare
https://github.com/saintdaddy/Vare-Obfuscator/blob/main/Vare.py
It says __VareObfuscator__ = '' at the top
"""

import ast
import base64
import marshal
import re
import zlib

from cryptography.fernet import Fernet

from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.deobf_utils import WEBHOOK_REGEX


def deobf(code: str) -> str:
    """
    Extracts the entire source code from code
    """
    key = ast.literal_eval(re.search(r'__mikey__\s*=\s*(([\'"]).+\2);mydata', code).group(1))
    data = ast.literal_eval(re.search(r'mydata\s*=\s*(([\'"]).+\2)', code).group(1))
    fernet = Fernet(base64.b64decode(key))
    return marshal.loads(
        zlib.decompress(base64.b32decode(base64.b64decode(
            base64.b64decode(base64.b64decode(base64.b32decode(
                base64.b64decode(fernet.decrypt(bytes.fromhex(data)))
            )))[::-1]
        )))
    ).decode()


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
