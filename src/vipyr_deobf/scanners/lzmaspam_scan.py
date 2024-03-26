import ast
from ast import Attribute, Call, Constant, Expr, Import, Load, Name, alias


class LZMAScanner(ast.NodeVisitor):
    def __init__(self):
        self.base64_import_found = False
        self.lzma_import_found = False
        self.payload_found = False

    def visit_Import(self, node):
        match node:
            case Import(
                names=[alias(name='base64')]
            ):
                self.base64_import_found = True
                return
            case Import(
                names=[alias(name='lzma')]
            ):
                self.lzma_import_found = True
                return

    def visit_Expr(self, node):
        match node:
            case Expr(
                value=Call(
                    func=Name(id='print', ctx=Load()),
                    args=[
                        Call(
                            func=Name(id='compile', ctx=Load()),
                            args=[
                                Call(
                                    func=Attribute(
                                        value=Name(id='lzma', ctx=Load()),
                                        attr='decompress',
                                        ctx=Load()),
                                    args=[
                                        Call(
                                            func=Attribute(
                                                value=Name(id='base64', ctx=Load()),
                                                attr='b64decode',
                                                ctx=Load()),
                                            args=[
                                                Constant(value=payload)],
                                            keywords=[])],
                                    keywords=[]),
                                Constant(value='<string>'),
                                Constant(value='exec')],
                            keywords=[])],
                    keywords=[])) if isinstance(payload, bytes):
                self.payload_found = True
                return


def scan_lzma(code: str):
    lzma_scanner = LZMAScanner()
    lzma_scanner.visit(ast.parse(code))
    return (
        lzma_scanner.base64_import_found
        and lzma_scanner.lzma_import_found
        and lzma_scanner.payload_found
    )
