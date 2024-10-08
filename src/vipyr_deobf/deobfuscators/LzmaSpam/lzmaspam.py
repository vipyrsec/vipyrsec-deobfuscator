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
from ast import Attribute, Call, Constant, Expr, Import, Name, alias

from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.deobf_utils import WEBHOOK_REGEX


def deobf(code: str) -> re.Match:
    """
    Extracts webhook from code
    """
    code = lzma.decompress(
        ast.literal_eval(
            re.search(
                r"(b'.+?')\n",
                lzma.decompress(base64.b64decode(
                    ast.literal_eval(
                        re.search(r"b'.+?'", code).group(0)
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


def format_results(webhook_match: re.Match) -> str:
    if webhook_match:
        return (f'Webhook:\n'
                f'{webhook_match.group(0)}')
    else:
        return "No webhook found."


class LZMAScanner(ast.NodeVisitor):
    def __init__(self):
        self.base64_import_found = False
        self.lzma_import_found = False
        self.payload_found = False

    def visit_Import(self, node):
        match node:
            case Import(names=[alias(name='base64')]):
                self.base64_import_found = True
                return
            case Import(names=[alias(name='lzma')]):
                self.lzma_import_found = True
                return

    def visit_Expr(self, node):
        match node:
            case Expr(
                value=Call(
                    func=Name(id='print'),
                    args=[
                        Call(
                            func=Name(id='compile'),
                            args=[
                                Call(
                                    func=Attribute(
                                        value=Name(id='lzma'),
                                        attr='decompress',
                                    ),
                                    args=[
                                        Call(
                                            func=Attribute(
                                                value=Name(id='base64'),
                                                attr='b64decode',
                                            ),
                                            args=[Constant(value=payload)],
                                        )
                                    ],
                                ),
                                Constant(value='<string>'),
                                Constant(value='exec')],
                        )
                    ],
                )
            ) if isinstance(payload, bytes):
                self.payload_found = True
                return


def scan(code: str):
    lzma_scanner = LZMAScanner()
    lzma_scanner.visit(ast.parse(code))
    return (
        lzma_scanner.base64_import_found
        and lzma_scanner.lzma_import_found
        and lzma_scanner.payload_found
    )


lzmaspam_deobf = Deobfuscator(deobf, format, scan)
register(lzmaspam_deobf)
