import ast
import logging
import re
import zlib
from ast import (
    Assign, Attribute, BinOp, BitXor, Break, Call, Compare, Constant,
    Eq, Expr, For, If, Import, ImportFrom, ListComp, Module, Name,
    Slice, Subscript, UnaryOp, comprehension, operator, unaryop
)

from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.deobf_utils import WEBHOOK_REGEX, known_funcs, op_dict

logger = logging.getLogger('deobf')
MAX_DEOBF_LIMIT = 30


class BlankObf2Deobf(ast.NodeTransformer):
    def __init__(self):
        self.namespace = {}

    def visit_List(self, node):
        self.generic_visit(node)
        # Folds lists of constants into a constant itself, to make them easier to handle
        if all(isinstance(elem, Constant) for elem in node.elts):
            # noinspection PyUnresolvedReferences
            return Constant(value=[const.value for const in node.elts])
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        match node:
            case Call(
                func=Name(id='bytes'),
                args=[Constant(value=const)],
            ):
                return Constant(value=bytes(const))
            case Call(
                func=Attribute(
                    value=Constant(value=bytes(byte_val)),
                    attr='decode',
                )
            ):
                return Constant(value=byte_val.decode())
            case Call(
                func=Name(id='getattr'),
                args=[
                    Call(
                        func=Name(id='__import__'),
                        args=[Constant(value=str(lib_name))],
                    ),
                    Constant(value=str(func_name)),
                ]
            ):
                if lib_name == 'builtins':
                    return Name(id=func_name)
                return Attribute(value=Name(id=lib_name), attr=func_name)
            case Call(
                func=Name(id='eval'),
                args=[Constant(value=str(val) | bytes(val))]
            ):
                return ast.parse(val, mode='eval').body
            case Call(
                func=Attribute(value=Name(id=lib_name), attr=func_name),
                args=[Constant(value=const)]
            ) if (lib_name, func_name) in known_funcs:
                return Constant(value=known_funcs[lib_name, func_name](const))
            case Call(
                func=Name(id='list'),
                args=[Constant(value=list()) as value],
            ):
                return value
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        match node:
            case Assign(
                targets=[Name(id=name)],
                value=Constant(value=value),
            ):
                self.namespace[name] = value
                return
        return node

    def visit_Name(self, node):
        if node.id in self.namespace:
            return Constant(value=self.namespace[node.id])
        return node

    def visit_Subscript(self, node):
        self.generic_visit(node)
        match node:
            case Subscript(
                value=Constant(value=target),
                slice=Constant(value=int(idx)),
            ):
                return Constant(value=target[idx])
            case Subscript(
                value=Constant(value=target),
                slice=Slice(
                    lower=Constant(value=lower) | (None as lower),
                    upper=Constant(value=upper) | (None as upper),
                    step=Constant(value=step) | (None as step),
                ),
            ):
                return Constant(value=target[lower:upper:step])
        return node

    def visit_ListComp(self, node):
        self.generic_visit(node)
        match node:
            case ListComp(
                elt=Call(func=Name(id='int')),
                generators=[
                    comprehension(iter=ListComp(
                        generators=[comprehension(iter=Constant(value=value))]
                    )), _
                ]
            ):
                return Constant(value=[int(num) for ip in value for num in ip.split('.')])
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        match node:
            case BinOp(
                left=Constant(value=left),
                op=operator() as op,
                right=Constant(value=right),
            ):
                return Constant(value=op_dict[type(op)](left, right))
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        match node:
            case UnaryOp(
                op=unaryop() as op,
                operand=Constant(value=operand),
            ):
                return Constant(value=op_dict[type(op)](operand))
        return node


class ImportExtractor(ast.NodeTransformer):
    def __init__(self):
        self.import_list = []

    def visit_Import(self, node):
        self.import_list.append(node)

    def visit_ImportFrom(self, node):
        self.import_list.append(node)


def deobf_first_layer(tree: ast.Module):
    deobfed_tree = BlankObf2Deobf().visit(tree)
    match deobfed_tree:
        case Module(
            body=[Expr(
                value=Call(
                    func=Name(id='exec'),
                    args=[Constant(value=bytes(payload))],
                )
            )]
        ):
            return ast.parse(payload)


def deobf_second_layer(tree: ast.Module):
    deobfed_tree = BlankObf2Deobf().visit(tree)
    match deobfed_tree:
        case Module(
            body=[For(
                body=[If(
                    test=Compare(
                        left=BinOp(
                            left=Constant(value=num1),
                            op=BitXor(),
                            right=Name(),
                        ),
                        ops=[Eq()],
                        comparators=[Constant(value=num2)],
                    ),
                    body=[Expr(value=Call(
                        func=Name(id='exec'),
                        args=[Call(
                            func=Attribute(
                                value=Name(id='zlib'),
                                attr='decompress',
                            ),
                            args=[Call(
                                func=Name(id='bytes'),
                                args=[Call(
                                    func=Name(id='map'),
                                    args=[
                                        _,
                                        Constant(value=payload),
                                    ]
                                )]
                            )]
                        )]
                    )), Break()]
                )]
            )]
        ):
            pad = num1 ^ num2
            return ast.parse(zlib.decompress(bytes([pad ^ i for i in payload])))


def deobf_third_layer(tree: ast.Module):
    deobfed_tree = BlankObf2Deobf().visit(tree)
    logging.info(f'Finished transforming third layer')
    match deobfed_tree:
        case Module(
            body=[Expr(
                value=Call(
                    func=Name(id='exec'),
                    args=[Call(
                        func=Name(id='compile'),
                        args=[Constant(value=bytes(payload)), *_],
                    )]
                )
            )
                  ]
        ):
            logging.info(f'Next layer located')
            return ast.parse(payload)


def deobf(code: str) -> tuple[bool, ast.Module]:
    tree = ast.parse(code)

    logger.info('Removing imports')
    import_ext = ImportExtractor()
    tree = import_ext.visit(tree)
    imports = import_ext.import_list
    logger.info(f'{len(imports)} imports found')

    for iteration in range(MAX_DEOBF_LIMIT):
        logging.info(f'Starting deobfuscation of layer {iteration}')
        match tree:
            case Module(body=[Expr(
                value=Constant(value=str(value))
            ), *_]) if re.search(r'blank\s*obf\s*v\s*2', value.lower()):
                logging.info('Deobfuscation finished')
                break
            case Module(body=[Assign(), Assign(), Assign(), Assign(), Expr()]):
                logging.info(f'Identified as first layer')
                new_tree = deobf_first_layer(tree)
            case Module(body=[Assign(), For()]):
                logging.info(f'Identified as second layer')
                new_tree = deobf_second_layer(tree)
            case Module(body=[Assign(), Assign(), Expr()]):
                logging.info(f'Identified as third layer')
                new_tree = deobf_third_layer(tree)
            case _:
                logging.error('Did not recognize layer')
                return False, tree
        if not new_tree:
            logging.error('Next layer not located, ending now')
            return False, tree
        tree = new_tree
    else:
        logging.error(f'Reached layer deobfuscation limit of {MAX_DEOBF_LIMIT}, ending now')
        return False, tree
    return True, tree


def format_results(results: tuple[bool, ast.Module]) -> str:
    status, tree = results
    if not status:
        logger.error('Code could not be fully deobfuscated: Attempting to return partial results now')
        return ast.unparse(tree)

    logger.info('Deobfuscation complete, formatting output')
    deobfed_code = ast.unparse(tree)
    webhooks = WEBHOOK_REGEX.findall(deobfed_code)
    if webhooks:
        logger.info('Webhooks found:')
        for webhook in webhooks:
            logger.info(f'{webhook}')
    return deobfed_code


def scan(code: str):
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


blankobf_v2_deobf = Deobfuscator(deobf, format_results, scan)
register(blankobf_v2_deobf)
