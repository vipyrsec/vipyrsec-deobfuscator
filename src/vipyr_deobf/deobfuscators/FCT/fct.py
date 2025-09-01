import ast
import base64
import binascii
import logging
import re
import zlib
from ast import (
    Assign, Attribute, Call, Constant, Expr, Lambda,
    Name, Slice, Subscript, UnaryOp, USub, arg, arguments
)
from io import StringIO

from vipyr_deobf.deobf_base import Deobfuscator, register
from vipyr_deobf.deobf_utils import BYTES_WEBHOOK_REGEX
from vipyr_deobf.exceptions import DeobfuscationFailError

logger = logging.getLogger('deobf')

MAX_DEOBF_LIMIT = 1000


class ByteStringFinder(ast.NodeVisitor):
    def __init__(self):
        self.results = []

    def visit_Constant(self, node):
        if isinstance(node.value, bytes):
            self.results.append(node.value)


def nab_surface_payload(surface_code: str) -> bytes:
    logger.info('Nabbing surface payload')
    try:
        tree = ast.parse(surface_code)
    # Other exceptions may appear, generalize this in the future
    except SyntaxError:
        logger.exception('Input text is not valid python')
        raise DeobfuscationFailError(
            surface_code = surface_code
        )
    bsf = ByteStringFinder()
    bsf.visit(tree)
    if len(bsf.results) > 1:
        logger.error('Multiple byte strings found')
        raise DeobfuscationFailError(
            bsf_results = bsf.results
        )
    elif not bsf.results:
        logger.error('No byte strings found in surface file')
        raise DeobfuscationFailError()
    return bsf.results[0]


def deobf_obf(obf_bytes: bytes) -> bytes:
    """
    Deobfuscates the obf function as defined in not_pyobfuscate.md
    """
    result = obf_bytes[::-1]
    try:
        try:
            result = base64.b64decode(result)
        except zlib.error:
            logger.warning('base64 failed, trying base32 now')
            result = base64.b32decode(result)
        result = zlib.decompress(result)
    except (binascii.Error, zlib.error):
        logger.exception(f'Error in deobf_obf when trying to deobfuscate bytes')
        raise DeobfuscationFailError(
            obf_bytes = obf_bytes
        )
    return result


def nab_bytes(marshalled_bytes: bytes) -> bytes:
    """
    Nabs the payload bytes from the marshalled code object
    Tries the shortcut with the hardcoded payload index first, and then tries regex
    """
    logger.info('Nabbing bytes from marshalled data')
    try:
        return index_nab_bytes(marshalled_bytes)
    except DeobfuscationFailError:
        logger.warning('Index failed, using regex (Expected)')
        return regex_nab_bytes(marshalled_bytes)


def index_nab_bytes(marshalled_bytes: bytes) -> bytes:
    """
    Uses the hardcoded index of 73 to grab the payload
    """
    logger.debug('Entering index_nab_bytes')
    header = marshalled_bytes[73:79]
    if header[:2] != b'\x02s':
        logger.warning('Bytes at index 73 is not header for bytes (Expected)')
        raise DeobfuscationFailError()
    payload_len = int.from_bytes(header[2:][::-1])
    payload_start = 79
    payload_end = payload_start + payload_len
    payload = marshalled_bytes[payload_start:payload_end]
    trailer = marshalled_bytes[payload_end:payload_end + 2]
    if trailer != b'N)':
        logger.error('Malformed marshal payload, length does not match trailer')
        raise DeobfuscationFailError(
            marshalled_bytes = marshalled_bytes
        )
    return payload


def regex_nab_bytes(marshalled_bytes: bytes) -> bytes:
    """
    Uses regex to grab the payload
    """
    logger.debug("Entering regex_nab_bytes (This shouldn't happen more than once)")
    # Keep track of the current idx, so we can discard '\x02s' headers when they appear within other strings
    current_idx = 0
    rtn_bytes = []
    for header in re.finditer(rb'\x02s([\x00-\xff]{4})', marshalled_bytes):
        if header.end() < current_idx:
            continue
        payload_start = header.end()
        payload_len = int.from_bytes(header.group(1)[::-1])
        payload = marshalled_bytes[payload_start: payload_start + payload_len]
        trailer = marshalled_bytes[payload_start + payload_len: payload_start + payload_len + 2]
        if trailer != b'N)':
            logger.warning('Malformed marshal payload, length does not match trailer')
            raise DeobfuscationFailError(
                marshalled_bytes = marshalled_bytes
            )
        rtn_bytes.append(payload)
        current_idx = payload_start + payload_len + 2
    if len(rtn_bytes) > 1:
        logger.error('Multiple payloads found in bytes (Expected)')
        raise DeobfuscationFailError(
            marshalled_bytes = marshalled_bytes,
            rtn_bytes = rtn_bytes,
        )
    elif not rtn_bytes:
        logger.warning('No payload found (Expected)')
        raise DeobfuscationFailError(
            marshalled_bytes = marshalled_bytes
        )
    return rtn_bytes[0]


def deobf(code: str) -> bytes:
    """
    Deobfuscates the not pyobfuscate schema
    :return: Marshalled code object of the source code
    """
    obf_bytes = nab_surface_payload(code)

    for iteration in range(MAX_DEOBF_LIMIT):
        logger.info(f'Deobfuscating bytes (iteration {iteration})')
        marshalled_bytes = deobf_obf(obf_bytes)
        if marshalled_bytes.startswith(b'exec((_)(b'):
            logger.debug('Byte string is not marshalled')
            obf_bytes = marshalled_bytes[11:-3]
            continue
        logger.debug('Byte string is marshalled')
        try:
            obf_bytes = nab_bytes(marshalled_bytes)
        except DeobfuscationFailError:
            return marshalled_bytes
        if not obf_bytes:
            return marshalled_bytes
    logging.warning(f'Reached byte deobfuscation limit of {MAX_DEOBF_LIMIT}, ending now')
    raise DeobfuscationFailError(
        marshalled_bytes = marshalled_bytes
    )


def format_results(marshalled_bytes: bytes) -> str:
    logger.info('Deobfuscation complete, formatting output')
    webhooks = BYTES_WEBHOOK_REGEX.findall(marshalled_bytes)

    rtn_string = StringIO()

    try:
        output = marshalled_bytes.decode()
    except UnicodeDecodeError:
        logger.info('Output appears to be marshalled')
        rtn_string.write(repr(marshalled_bytes))
    else:
        logger.info('Output appears to be normal python')
        rtn_string.write(output)

    if webhooks:
        logger.info('Webhooks found:')
        for webhook in webhooks:
            logger.info(f'{webhook.decode()}')

    return rtn_string.getvalue()


def match_inner_underscore_function(node: ast.Call):
    match node:
        case Call(
            func=Attribute(
                value=Call(
                    func=Name(id='__import__'),
                    args=[Constant(value='zlib')]
                ),
                attr='decompress',
            ),
            args=[
                Call(
                    func=Attribute(
                        value=Call(
                            func=Name(id='__import__'),
                            args=[Constant(value='base64')]
                        ),
                        attr='b64decode',
                    ),
                    args=[
                        Subscript(
                            value=Name(id='__'),
                            slice=Slice(
                                step=UnaryOp(op=USub(), operand=Constant(value=1))),
                        )
                    ]
                )
            ]
        ):
            return True
    return False


class FCTScanner(ast.NodeVisitor):
    def __init__(self):
        self.underscore_function_found = False
        self.payload_found = False

    def visit_Assign(self, node):
        match node:
            case Assign(
                targets=[Name(id='_')],
                value=Lambda(
                    args=arguments(args=[arg(arg='__')]),
                    body=Call(
                        func=Attribute(
                            value=Call(
                                func=Name(id='__import__'),
                                args=[Constant(value='marshal')]
                            ),
                            attr='loads',
                        ),
                        args=[body]
                    ) | body
                )
            ) if match_inner_underscore_function(body):
                self.underscore_function_found = True
                return

    def visit_Expr(self, node):
        match node:
            case Expr(
                value=Call(
                    func=Name(id='exec'),
                    args=[
                        Call(
                            func=Name(id='_'),
                            args=[Constant(value=payload)]
                        )
                    ]
                )
            ) if isinstance(payload, bytes):
                self.payload_found = True
                return


def scan(code: str):
    fct_scanner = FCTScanner()
    fct_scanner.visit(ast.parse(code))
    return (
        fct_scanner.underscore_function_found
        and fct_scanner.payload_found
    )


fct_deobf = Deobfuscator(deobf, format_results, scan)
register(fct_deobf)
