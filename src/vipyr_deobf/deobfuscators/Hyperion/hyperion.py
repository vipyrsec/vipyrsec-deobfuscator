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
from ast import Assign, Attribute, Call, Constant, Name, Tuple

from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.deobf_utils import WEBHOOK_REGEX


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
                                    value=Call(func=Name(id='__import__'), args=[Constant(value='zlib')]),
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
                            value=Call(func=Name(id='__import__'), args=[Constant(value='zlib')]),
                            attr='decompress'),
                        args=[Constant(value=payload)])]):
                value = base64.b64decode(zlib.decompress(payload))
                return Constant(value=value)
            case _:
                return self.generic_visit(node)


def deobf(code: str) -> list[str]:
    """
    Extracts all strings containing 'https' from the code
    """
    no_frosting = ast.unparse(HyperionB64zlibBytes().visit(ast.parse(code)))
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


def format_results(urls: list[str]) -> str:
    webhooks = [url for url in urls if re.search(WEBHOOK_REGEX, url)]
    if webhooks:
        return ('Webhooks:\n'
                + '\n'.join(webhooks))
    else:
        return ('No webhooks found, displaying all urls:\n'
                + '\n'.join(urls))


class HyperionScanner(ast.NodeVisitor):
    def __init__(self):
        self.signature_found = False

    def visit_Assign(self, node):
        match node:
            case Assign(
                targets=[Name(id='__obfuscator__')],
                value=Constant(value='Hyperion'),
            ) | Assign(
                targets=[Name(id='__authors__')],
                value=Tuple(
                    elts=[
                        Constant(value='billythegoat356'),
                        Constant(value='BlueRed')
                    ],
                )
            ) | Assign(
                    targets=[Name(id='__github__')],
                    value=Constant(value='https://github.com/billythegoat356/Hyperion')
            ):
                self.signature_found = True
                return


COMMENT_REGEX = re.compile(
    r'# sourcery skip: collection-to-bool, remove-redundant-boolean, remove-redundant-except-handler'
)


def scan(code: str):
    if COMMENT_REGEX.search(code):
        return True
    hyp_scanner = HyperionScanner()
    hyp_scanner.visit(ast.parse(code))
    return hyp_scanner.signature_found


hyperion_deobf = Deobfuscator(deobf, format_results, scan)
register(hyperion_deobf)
