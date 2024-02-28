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
import base64
import binascii
import re
import zlib
from ast import *
from typing import TextIO

from vipyr_deobf.utils import WEBHOOK_REGEX


class HyperionB64zlibBytes(ast.NodeTransformer):
    """
    Temp transformer for the base64 zlib frosting until we get the better oven
    """

    def visit_Call(self, node: Call):
        match node:
            case Call(
                func=Attribute(
                  value=Call(
                    func=Attribute(
                      value=Call(func=Name(id='__import__'), args=[Constant(value='base64')]),
                      attr='b64decode'),
                    args=[
                      Call(
                        func=Attribute(
                          value=Call(func=Name(id='__import__'),args=[Constant(value='zlib')]),
                          attr='decompress'),
                        args=[Constant(value=payload)])]),
                  attr='decode')):
                value = base64.b64decode(zlib.decompress(payload)).decode()
                return Constant(value=value)
            case Call(
                    func=Attribute(
                      value=Call(func=Name(id='__import__'), args=[Constant(value='base64')]),
                      attr='b64decode'),
                    args=[
                      Call(
                        func=Attribute(
                          value=Call(func=Name(id='__import__'),args=[Constant(value='zlib')]),
                          attr='decompress'),
                        args=[Constant(value=payload)])]):
                value = base64.b64decode(zlib.decompress(payload))
                return Constant(value=value)
            case _:
                node.func = self.visit(node.func)
                node.args = [self.visit(n) for n in node.args]
                node.keywords = [self.visit(n) for n in node.keywords]
                return node


def hyperion_deobf(file: TextIO) -> list[str]:
    """
    Extracts all strings containing 'https' from the code
    """
    no_frosting = ast.unparse(HyperionB64zlibBytes().visit(ast.parse(file.read())))
    code = zlib.decompress(
        b''.join(
            ast.literal_eval(byte_string)
            for byte_string, _ in re.findall(r"(?<!i)(b(['\"]).+\2)", no_frosting)
        )
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


def format_hyperion(urls: list[str]) -> str:
    webhooks = [url for url in urls if re.search(WEBHOOK_REGEX, url)]
    if webhooks:
        return ('Webhooks:\n'
                + '\n'.join(webhooks))
    else:
        return ('No webhooks found, displaying all urls:\n'
                + '\n'.join(urls))


if __name__ == '__main__':
    pass
