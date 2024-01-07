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
from typing import TextIO

from cryptography.fernet import Fernet
from ..utils import WEBHOOK_REGEX


def vore_deobf(file: TextIO) -> str:
    """
    Extracts the entire source code from code
    """
    code = file.read()
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


def format_vore(result: str) -> str:
    return result + '\n\n' + '\n'.join(re.findall(WEBHOOK_REGEX, result))


if __name__ == '__main__':
    pass
