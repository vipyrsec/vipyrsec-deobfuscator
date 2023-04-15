#!/usr/bin/python3
"""
Deobfuscator for the Hyperion obfuscation schema
https://github.com/billythegoat356/Hyperion
Hyperion is pretty easy to recognize considering it advertises itself at the top of the code
(Forcibly btw if you try and remove it the code doesn't run)
If the malware author somehow removed it, then lines like
    from math import prod as Hypothesis
    class _theory:
    except Exception as _floor:
        if 365101 > 7435378:
            _theory.execute(code = Walk(_floor))
        elif 337143 > 2680668:
            _theory(_modulo = -56047 * -45510).Calculate(CallFunction = _builtins._system * 14696)
and generally weird looking pseudo-math code is probably Hyperion
"""

import ast
import binascii
import re
import zlib
from typing import NoReturn, TextIO


def hyperion_deobf(file: TextIO) -> list[str]:
    """
    Extracts all strings containing 'https' from the code
    """
    code = zlib.decompress(
        b''.join(map(
            ast.literal_eval,
            re.findall(r"b['\"].+['\"]", file.read())
        ))
    ).decode()
    results = [
        ast.literal_eval(url)
        for byte_string in
        re.findall(
            r"]=.+\W(b'.+?')",
            code
        )
        if 'https' in (url := binascii.unhexlify(ast.literal_eval(byte_string)).decode())
    ]
    return results


def format_hyperion(urls: list[str]) -> NoReturn:
    webhooks = [url for url in urls if 'https://discord.com/api/webhooks' in url]
    if webhooks:
        return ('Webhooks:\n'
                + '\n'.join(webhooks))
    else:
        return ('No webhooks found, displaying all urls:\n'
                + '\n'.join(urls))


if __name__ == '__main__':
    pass
