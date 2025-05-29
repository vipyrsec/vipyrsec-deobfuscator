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

from __future__ import annotations

import ast
import base64
import binascii
import logging
import re
import zlib
from ast import (
    Add,
    And,
    Assign,
    Attribute,
    BinOp,
    BoolOp,
    Call,
    Constant,
    Expr,
    Invert,
    Lambda,
    Module,
    Name,
    NodeVisitor,
    Not,
    Or,
    Slice,
    Sub,
    Subscript,
    Try,
    UAdd,
    UnaryOp,
    USub,
    arg,
    arguments,
    keyword,
    stmt,
)
from collections import ChainMap
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from typing_extensions import override

from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.exceptions import DeobfuscationFailError

logger = logging.getLogger('hyperion')


class FLB64zlib(ast.NodeTransformer):
    """Collapses __import__('base64').b64decode(__import__('zlib').decompress(...))"""

    @override
    def visit_Call(self, node: Call):
        match node:
            case Call(
                func=Attribute(
                    value=Call(
                        func=Attribute(
                            value=Call(
                                func=Name(id='__import__'),
                                args=[Constant(value='base64')],
                            ),
                            attr='b64decode',
                        ),
                        args=[
                            Call(
                                func=Attribute(
                                    value=Call(
                                        func=Name(id='__import__'),
                                        args=[Constant(value='zlib')],
                                    ),
                                    attr='decompress',
                                ),
                                args=[Constant(value=payload)],
                            )
                        ],
                    ),
                    attr='decode',
                )
            ):
                value = base64.b64decode(zlib.decompress(payload)).decode()
                return Constant(value=value)
            case Call(
                func=Attribute(
                    value=Call(
                        func=Name(id='__import__'),
                        args=[Constant(value='base64')],
                    ),
                    attr='b64decode',
                ),
                args=[
                    Call(
                        func=Attribute(
                            value=Call(
                                func=Name(id='__import__'),
                                args=[Constant(value='zlib')],
                            ),
                            attr='decompress',
                        ),
                        args=[Constant(value=payload)],
                    )
                ],
            ):
                value = base64.b64decode(zlib.decompress(payload))
                return Constant(value=value)
            case _:
                return self.generic_visit(node)


@dataclass(slots=True)
class FLNabBytes(NodeVisitor):
    bytes: BytesIO = field(default_factory=BytesIO)

    @override
    def visit_Call(self, node: Call):
        match node:
            case Call(
                func=Attribute(),
                args=[],
                keywords=[
                    keyword(value=Constant(value=str())),
                    keyword(value=Constant(value=bytes(payload))),
                ],
            ):
                _ = self.bytes.write(payload)
            case _:
                pass


def deobf_first_layer(ast_tree: Module) -> str:
    """Deobfuscate the outer layer of hyperion
    The outer layer just hides some byte strings in some heavily indented
    lines, so we just find these byte strings and zlib.decompress them into
    the second layer. In some samples, these byte strings get b64 encoded
    and compressed (frosting), so we also run a quick transformer to undo that.

    Args:
        ast_tree: ast.parse(code)

    Returns:
        Second layer as a string
    """
    logger.info('Running b64+zlib frosting remover')
    defrosted = FLB64zlib().visit(ast_tree)
    logger.info('Nabbing first layer bytes')
    byte_nabber = FLNabBytes()
    byte_nabber.visit(defrosted)
    second_layer_bytes = byte_nabber.bytes.getvalue()
    if not second_layer_bytes:
        logger.error('First layer bytes not found')
        raise DeobfuscationFailError()
    return zlib.decompress(second_layer_bytes).decode()


@dataclass(slots=True)
class MockObj:
    name: str
    obj: Any = None
    func: Callable[..., MockObj | None] | None = None
    items: dict[str, MockObj] = field(default_factory=dict)
    attrs: dict[str, MockObj] = field(default_factory=dict)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        logger.debug(
            f'Calling {self.name} with {len(args)} args and kwargs {", ".join(kwargs)}'
        )
        if self.func is None:
            raise ValueError(f'Mock object {self.name} cannot be called')
        return self.func(*args, **kwargs)

    def getitem(self, key: str) -> Any:
        logger.debug(f'Retrieving {key=} from {self.name}')
        if key not in self.items:
            raise ValueError(f'Key {key} not in object {self.name}')
        return self.items[key]

    def getattr(self, attr: str) -> Any:
        logger.debug(f'Retrieving {attr=} from {self.name}')
        if attr not in self.attrs:
            raise ValueError(f'Attr {attr} not in object {self.name}')
        return self.attrs[attr]

    @override
    def __repr__(self) -> str:
        return f'<{self.name}{f": {self.obj}" if self.obj is not None else ""}>'


def mock_func(func: Callable[..., Any]) -> Callable[..., MockObj]:
    def inner(*args: Any, **kwargs: Any) -> MockObj:
        return conv_type_to_mock(func(*args, **kwargs))

    return inner


def make_mock(name: str, type_name: str, *methods: str) -> Callable[[Any], MockObj]:
    def inner(obj: Any) -> MockObj:
        return MockObj(
            name,
            obj=obj,
            attrs={
                method: MockObj(
                    f'{type_name}.{method}', func=mock_func(getattr(obj, method))
                )
                for method in methods
            },
        )

    return inner


MockStrList = make_mock('MockStrList', 'list', '__getitem__', 'index')
MockStr = make_mock('MockStr', 'str', 'join')
MockInt = make_mock('MockInt', 'int', '__neg__', '__pos__')
MockBytes = make_mock('MockBytes', 'bytes', 'decode')
MockFloat = make_mock('MockFloat', 'float')
MockCodeObj = make_mock('MockCodeObj', 'code')


def conv_type_to_mock(obj: object) -> MockObj:
    match obj:
        case str(string):
            return MockStr(string)
        case int(num):
            return MockInt(num)
        case float(num):
            return MockFloat(num)
        case bytes(b):
            return MockBytes(b)
        case [*items] if all(isinstance(item, str) for item in items):  # type: ignore[reportUnknownVariableType]
            items: list[str]
            return MockStrList(items)
        case _:
            raise ValueError(f'Unknown constant of type {type(obj)}')


def mock_dir(obj: object) -> MockObj:
    match obj:
        case MockObj():
            return MockStrList([*obj.attrs.keys()])
        case _:
            raise ValueError(f'Unexpected obj {type(obj)} passed to dir')


def mock_import(lib: str) -> MockObj | None:
    return mock_libs.get(lib)


def mock_getattr(obj: object, attr: str) -> MockObj:
    match obj, attr:
        case MockObj(), str():
            return obj.getattr(attr)
        case _:
            raise ValueError(f'Unexpected obj {type(obj)} passed to getattr')


def mock_compile(code: str, *_: Any, **__: Any) -> MockObj:
    return MockCodeObj(code)


def mock_vars(obj: object = None) -> MockObj:
    if obj is not None:
        raise TypeError(f'Mock vars does not support arguments yet, received {obj!r}')
    return MockObj('vars', items=mocks)


mocks: dict[str, MockObj] = {
    'globals': MockObj('globals_func', func=lambda: MockObj('globals', items=mocks)),
    'getattr': MockObj('getattr', func=mock_getattr),
    'dir': MockObj('dir', func=mock_dir),
    'vars': MockObj('vars', func=mock_vars),
    'locals': MockObj('locals_func', func=lambda: MockObj('locals', items=mocks)),
    '__import__': MockObj('__import__', func=mock_import),
    'float': MockObj('float', func=mock_func(float)),
    'True': MockObj('True', obj=True),
    'False': MockObj('False', obj=False),
    'str': MockObj('str', func=mock_func(str)),
    'compile': MockObj('compile', func=mock_compile),
    'bool': MockObj('bool', func=mock_func(bool)),
    'exec': MockObj('exec'),
    'eval': MockObj('eval'),
}
mock_libs: dict[str, MockObj] = {
    'builtins': MockObj('builtins', attrs=mocks),
    'binascii': MockObj(
        'binascii',
        attrs={
            'unhexlify': MockObj('unhexlify', func=mock_func(binascii.unhexlify)),
        },
    ),
}


@dataclass(slots=True)
class SecondLayerTransformer(ast.NodeTransformer):
    var_dict: MutableMapping[str, MockObj] = field(
        default_factory=lambda: ChainMap({}, mocks)  # type: ignore[reportAssignmentType]
    )

    @override
    def visit_Constant(self, node: Constant) -> Constant:
        try:
            return Constant(conv_type_to_mock(node.value))
        except ValueError:
            logger.info(f'Constant of type {type(node.value)} found')
            return node

    @override
    def visit_Name(self, node: Name) -> Name | Constant:
        self.generic_visit(node)
        if node.id in self.var_dict:
            return Constant(self.var_dict[node.id])
        return node

    @override
    def visit_Subscript(self, node: Subscript) -> Subscript | Constant:
        self.generic_visit(node)
        match node:
            case Subscript(
                value=Constant(MockObj('MockStr', obj=str(value))),
                slice=Slice(
                    lower=Constant(MockObj('MockInt', obj=int(lower)))
                    | (None as lower),
                    upper=Constant(MockObj('MockInt', obj=int(upper)))
                    | (None as upper),
                    step=Constant(MockObj('MockInt', obj=int(step))) | (None as step),
                ),
            ):
                return Constant(MockStr(value[lower:upper:step]))
            case Subscript(
                value=Constant(MockObj('globals' | 'locals' | 'vars')),
                slice=Constant(MockObj('MockStr', obj=str(key))),
            ):
                if key not in self.var_dict:
                    logger.exception(f'Failed getitem {key} from globals')
                    return node
                return Constant(self.var_dict[key])
            case Subscript(
                value=Constant(MockObj() as obj),
                slice=Constant(MockObj('MockStr', obj=str(key))),
            ):
                try:
                    return Constant(obj.getitem(key))
                except ValueError:
                    logger.exception('Failed getitem')
                    return node
            case Subscript(
                value=Constant(MockObj('MockStrList', obj=seq)),
                slice=Constant(MockObj('MockInt', obj=int(idx))),
            ):
                return Constant(MockStr(seq[idx]))
            case _:
                return node

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> UnaryOp | Constant:
        self.generic_visit(node)
        match node:
            case UnaryOp(
                op=op,
                operand=Constant(
                    MockObj('MockInt', obj=int(num))
                    | MockObj('True' | 'False', obj=bool(num))
                ),
            ):
                match op:
                    case UAdd():
                        num = +num
                    case USub():
                        num = -num
                    case Invert():
                        num = ~num  # type: ignore[reportDeprecated]
                    case Not():
                        num = not num
                    case _:
                        return node
                return Constant(MockInt(num))
            case _:
                return node

    @override
    def visit_Attribute(self, node: Attribute) -> Attribute | Constant:
        self.generic_visit(node)
        match node:
            case Attribute(
                value=Constant(MockObj() as obj),
                attr=str(attr),
            ):
                try:
                    return Constant(obj.getattr(attr))
                except ValueError:
                    logger.exception('Failed getattr')
                    return node
            case _:
                return node

    @override
    def visit_Assign(self, node: Assign) -> Any:
        self.generic_visit(node)
        match node:
            case Assign(
                targets=[
                    Subscript(
                        value=Constant(MockObj('globals' | 'locals' | 'vars')),
                        slice=Constant(MockObj('MockStr', obj=str(name))),
                    )
                ],
                value=Constant(value),
            ):
                logger.info(f'Assigning {name} = {value!r}')
                self.var_dict[name] = value
                return None
            case _:
                return node

    @override
    def visit_Expr(self, node: Expr) -> Expr | stmt | list[stmt]:
        self.generic_visit(node)
        match node:
            case Expr(
                Call(
                    func=Constant(MockObj('exec')),
                    args=[Constant(MockObj('MockStr', obj=code))],
                )
            ):
                return self.visit(ast.parse(code, mode='exec')).body
            case Expr(
                Call(
                    func=Constant(MockObj('exec')),
                    args=[Constant(MockObj('MockCodeObj', obj=code))],
                )
            ):
                return self.visit(ast.parse(code, mode='exec')).body
            case _:
                return node

    @override
    def visit_Call(self, node: Call) -> Call | Constant:
        self.generic_visit(node)
        match node:
            case Call(
                func=Constant(MockObj('eval')),
                args=[Constant(MockObj('MockStr', obj=code))],
            ):
                return self.visit(ast.parse(code, mode='eval')).body
            case Call(
                func=Constant(MockObj('eval')),
                args=[Constant(MockObj('MockCodeObj', obj=code))],
            ):
                return self.visit(ast.parse(code, mode='eval')).body
            case Call(
                func=Constant(MockObj() as func),
                args=[*args_list],
                keywords=[*kwargs_list],
            ) if func.func is not None:
                args: list[Any] = []
                for arg in args_list:
                    match arg:
                        case Constant(MockObj(obj=None) as value):
                            args.append(value)
                        case Constant(MockObj(obj=value)):
                            args.append(value)
                        case _:
                            return node
                kwargs: dict[str, Any] = {}
                for kwarg in kwargs_list:
                    match kwarg:
                        case keyword(
                            arg=str(key),
                            value=Constant(MockObj(obj=None) as value),
                        ):
                            kwargs[key] = value
                        case keyword(
                            arg=str(key),
                            value=Constant(MockObj(obj=value)),
                        ):
                            kwargs[key] = value
                        case _:
                            return node
                try:
                    res = func(*args, **kwargs)
                except (ValueError, TypeError):
                    logger.exception('Exception encountered during function evaluation')
                    logger.error(ast.dump(node, indent=2))
                    raise
                else:
                    if res is None:
                        return node
                    return Constant(res)
            case _:
                return node

    @override
    def visit_BinOp(self, node: BinOp) -> BinOp | Constant:
        self.generic_visit(node)
        match node:
            case BinOp(
                left=Constant(MockObj('MockInt', obj=int(left))),
                right=Constant(MockObj('MockInt', obj=int(right))),
                op=op,
            ):
                match op:
                    case Add():
                        num = left + right
                    case Sub():
                        num = left - right
                    case _:
                        return node
                return Constant(MockInt(num))
            case _:
                return node

    @override
    def visit_BoolOp(self, node: BoolOp) -> Any:
        self.generic_visit(node)
        match node:
            case BoolOp(
                op=op,
                values=[*values],
            ):
                nums: list[int] = []
                for value in values:
                    match value:
                        case Constant(MockObj('True' | 'False', obj=bool(num))):
                            nums.append(num)
                        case Constant(MockObj('MockInt', obj=int(num))):
                            nums.append(num)
                        case _:
                            return node
                match op:
                    case And():
                        res = all(nums)
                    case Or():
                        res = any(nums)
                    case _:
                        return node
                return Constant(MockInt(res))
            case _:  # type: ignore[reportUnnecessaryComparison]
                return node  # type: ignore[reportUnreachable]

    @override
    def visit_Lambda(self, node: Lambda) -> Lambda | Constant:
        self.generic_visit(node)
        match node:
            case Lambda(
                args=arguments(args=[arg(arg=str())]),
                body=Constant(value=MockObj(('globals' | 'locals' | 'vars') as name)),
            ):

                def inner(_: Any) -> MockObj:
                    return MockObj(name, items=mocks)

                return Constant(MockObj(f'fake_{name}', func=inner))
            case _:
                return node


def revert_mocks(obj: MockObj) -> Constant | Name:
    match obj:
        case MockObj('MockStr', obj=str(string)):
            return Constant(string)
        case MockObj('MockInt', obj=int(num)):
            return Constant(num)
        case MockObj('MockFloat', obj=float(num)):
            return Constant(num)
        case MockObj('MockBytes', obj=bytes(num)):
            return Constant(num)
        case MockObj(('str' | 'eval' | 'exec' | '__import__' | 'unhexlify') as name):
            return Name(id=name)
        case MockObj(name):
            logger.info(f'Could not identify object {name}')
            return Name(id=name)


@dataclass(slots=True)
class SecondLayerCleanup(ast.NodeTransformer):
    var_dict: MutableMapping[str, MockObj]

    @override
    def visit_Name(self, node: Name) -> Name | Constant:
        match node:
            case Name(id=str(name)) if name in self.var_dict:
                return revert_mocks(self.var_dict[name])
            case _:
                return node

    @override
    def visit_Constant(self, node: Constant) -> Any:
        match node:
            case Constant(MockObj() as obj):
                return revert_mocks(obj)
            case _:
                return node


def deobf_second_layer(ast_tree: Module) -> str:
    match ast_tree:
        case Module(body=[Try(), *_]):
            logger.info('Try statement exists, continuing with deobf')
        case _:
            logger.error('Try statement could not be found')
            raise DeobfuscationFailError()
    ast_tree.body.pop(0)
    slt = SecondLayerTransformer()
    slc = SecondLayerCleanup(slt.var_dict)
    payload = slc.visit(slt.visit(ast_tree))
    return ast.unparse(payload)


def full_hyperion_deobf(first_layer: str) -> str:
    logger.info('Deobfuscating first layer')
    second_layer = deobf_first_layer(ast.parse(first_layer))
    logger.info('First layer successfully deobfuscated, deobfuscating second layer')
    try:
        return deobf_second_layer(ast.parse(second_layer))
    except DeobfuscationFailError:
        logger.error(
            'Second layer could not be deobfuscated, returning obfuscated second layer'
        )
        return second_layer


def format_results(code: str) -> str:
    return code


@dataclass
class HyperionScanner(ast.NodeVisitor):
    signature_found: bool = False

    @override
    def visit_Assign(self, node: Assign):
        match node:
            case (
                Assign(
                    targets=[Name(id='__obfuscator__')],
                )
                | Assign(
                    targets=[Name(id='__authors__')],
                )
                | Assign(
                    targets=[Name(id='__github__')],
                )
            ):
                self.signature_found = True
                return
            case _:
                self.generic_visit(node)


COMMENT_REGEX = re.compile(
    r'# sourcery skip: collection-to-bool, remove-redundant-boolean, remove-redundant-except-handler'
)


def scan(code: str):
    if COMMENT_REGEX.search(code):
        return True
    hyp_scanner = HyperionScanner()
    hyp_scanner.visit(ast.parse(code))
    return hyp_scanner.signature_found


hyperion_deobf = Deobfuscator(full_hyperion_deobf, format_results, scan)
register(hyperion_deobf)
