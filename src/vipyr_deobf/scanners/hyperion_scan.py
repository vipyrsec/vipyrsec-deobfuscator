import ast
import re
from ast import Assign, Constant, Name, Tuple


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


def scan_hyperion(code: str):
    if COMMENT_REGEX.search(code):
        return True
    hyp_scanner = HyperionScanner()
    hyp_scanner.visit(ast.parse(code))
    return hyp_scanner.signature_found
