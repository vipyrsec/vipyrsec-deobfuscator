import ast
import base64
import operator
import re
import zlib
from ast import Constant
from collections.abc import Callable

WEBHOOK_REGEX = re.compile(
    r'https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/api(?:/v\d{1,2})?/webhooks/\d{17,21}/[\w-]{68}'
)
BYTES_WEBHOOK_REGEX = re.compile(
    br'https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/api(?:/v\d{1,2})?/webhooks/\d{17,21}/[\w-]{68}'
)

known_funcs = {
    ('base64', 'b64decode'): base64.b64decode,
    ('zlib', 'decompress'): zlib.decompress,
}

op_dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
    ast.BitOr: operator.or_,
    ast.BitXor: operator.xor,
    ast.BitAnd: operator.and_,
    ast.MatMult: operator.matmul,

    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
    ast.Invert: operator.invert,
}


class StringCollapser(ast.NodeTransformer):
    """
    Collapses Constant(value=str()) to some smaller str()
    To help with seeing ast code structure
    """

    def __init__(self, renamer: str | Callable[[str], str] = 'a'):
        """
        :param renamer: Either a string to rename everything to, or a function that receives the original
        variable name as argument and outputs the new name
        """
        self.renamer = (lambda _: renamer) if isinstance(renamer, str) else renamer

    def visit_Constant(self, node):
        match node:
            case Constant(value=str(value)):
                return Constant(value=self.renamer(value))
        return node
