import ast
from ast import (Assign, Attribute, Call, Constant, Expr, Lambda, Load, Name,
                 Slice, Store, Subscript, UnaryOp, USub, arg, arguments)


class FCTScanner(ast.NodeVisitor):
    def __init__(self):
        self.underscore_function_found = False
        self.payload_found = False

    def visit_Assign(self, node):
        match node:
            case Assign(
                targets=[
                    Name(id='_', ctx=Store())],
                value=Lambda(
                    args=arguments(
                        args=[
                            arg(arg='__')],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]),
                    body=Call(
                        func=Attribute(
                            value=Call(
                                func=Name(id='__import__', ctx=Load()),
                                args=[
                                    Constant(value='zlib')],
                                keywords=[]),
                            attr='decompress',
                            ctx=Load()),
                        args=[
                            Call(
                                func=Attribute(
                                    value=Call(
                                        func=Name(id='__import__', ctx=Load()),
                                        args=[
                                            Constant(value='base64')],
                                        keywords=[]),
                                    attr='b64decode',
                                    ctx=Load()),
                                args=[
                                    Subscript(
                                        value=Name(id='__', ctx=Load()),
                                        slice=Slice(
                                            step=UnaryOp(
                                                op=USub(),
                                                operand=Constant(value=1))),
                                        ctx=Load())],
                                keywords=[])],
                        keywords=[]))):
                self.underscore_function_found = True
                return

    def visit_Expr(self, node):
        match node:
            case Expr(
                value=Call(
                    func=Name(id='exec', ctx=Load()),
                    args=[
                        Call(
                            func=Name(id='_', ctx=Load()),
                            args=[
                                Constant(value=payload)],
                            keywords=[])],
                    keywords=[])) if isinstance(payload, bytes):
                self.payload_found = True
                return


def scan_fct(code: str):
    fct_scanner = FCTScanner()
    fct_scanner.visit(ast.parse(code))
    return (
        fct_scanner.underscore_function_found
        and fct_scanner.payload_found
    )
