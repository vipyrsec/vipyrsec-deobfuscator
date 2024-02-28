"""
Deobfuscator for an obfuscation schema that has heavy use of lzma.decompress and base64.b64decode
Example: https://hst.sh/raw/ojucipihoc
If the file begins with
    import base64
    import lzma
    exec(compile(lzma.decompress(base64.b64decode(...))))
Then it's likely this obfuscation schema
"""

import ast
import base64
import codecs
import lzma
import re
from typing import TextIO

from vipyr_deobf.utils import WEBHOOK_REGEX


def deobf_lzma_b64(file: TextIO) -> re.Match:
    """
    Extracts webhook from code
    """
    code = lzma.decompress(
        ast.literal_eval(
            re.search(
                r"(b'.+?')\n",
                lzma.decompress(base64.b64decode(
                    ast.literal_eval(
                        re.search(r"b'.+?'", file.read()).group(0)
                    )
                )).decode()
            ).group(1)
        )
    ).decode()
    var_code, mal_code = re.split(r';(?=[^;]+$)', code)
    doggo = {k: v for k, v in re.findall(r'(_{3,})="(.+?)"(?:;|$)', var_code)}
    a, b, c, d = map(doggo.get, re.findall(r'_{3,}', mal_code))
    webhook_match = re.search(
        WEBHOOK_REGEX,
        str(base64.b64decode(
            codecs.decode(a, 'rot13') + b + c[::-1] + d
        ))
    )
    return webhook_match


def format_lzma_b64(webhook_match: re.Match) -> str:
    if webhook_match:
        return (f'Webhook:\n'
                f'{webhook_match.group(0)}')
    else:
        return "No webhook found."


if __name__ == '__main__':
    pass
