import ast
from ast import Assign, Break, Expr, For, If, Import, ImportFrom, Module


def scan_blankobf2(code: str):
    tree = ast.parse(code)
    match tree:
        case Module(
            body=[
                *imports,
                Assign(),
                Assign(),
                Assign(),
                Assign(),
                Expr(),
            ]
        ) if all(isinstance(imp, Import | ImportFrom) for imp in imports):
            return True
        case Module(
            body=[Assign(), For(body=If(body=[Expr(), Break()]))]
        ):
            return True
    return False
