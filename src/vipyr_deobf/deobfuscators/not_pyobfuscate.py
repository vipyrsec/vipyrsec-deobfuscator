import ast
import base64
import binascii
import re
import zlib
from io import StringIO
from typing import TextIO

from vipyr_deobf.exceptions import DeobfuscationFailError
from vipyr_deobf.utils import BYTES_WEBHOOK_REGEX


class ByteStringFinder(ast.NodeVisitor):
    def __init__(self):
        self.results = []

    def visit_Constant(self, node):
        if isinstance(node.value, bytes):
            self.results.append(node.value)


def nab_surface_payload(surface_code: str) -> bytes:
    try:
        tree = ast.parse(surface_code)
    # Other exceptions may appear, generalize this in the future
    except SyntaxError as exc:
        raise DeobfuscationFailError(
            'Input text is not valid python',
            severity='critical',
            status='expected',
            exc=exc,
        )
    bsf = ByteStringFinder()
    bsf.visit(tree)
    if len(bsf.results) > 1:
        raise DeobfuscationFailError(
            f'Multiple byte strings found:\n{'\n'.join(map(repr, bsf.results))}',
            severity='medium',
            status='expected',
        )
    elif not bsf.results:
        raise DeobfuscationFailError(
            'No byte strings found in surface file',
            severity='critical',
            status='expected',
        )
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
            result = base64.b32decode(result)
        result = zlib.decompress(result)
    except (binascii.Error, zlib.error) as exc:
        raise DeobfuscationFailError(
            f'Error in deobf_obf when trying to deobfuscate {obf_bytes}',
            severity='critical',
            status='expected',
            exc=exc,
        )
    return result


def nab_bytes(marshalled_bytes: bytes) -> bytes:
    """
    Nabs the payload bytes from the marshalled code object
    Tries the shortcut with the hardcoded payload index first, and then tries regex
    """
    try:
        return index_nab_bytes(marshalled_bytes)
    except DeobfuscationFailError:
        pass
    # TODO: in the future, raise a warning if this happens
    return regex_nab_bytes(marshalled_bytes)


def index_nab_bytes(marshalled_bytes: bytes) -> bytes:
    """
    Uses the hardcoded index of 73 to grab the payload
    """
    header = marshalled_bytes[73:79]
    if header[:2] != b'\x02s':
        raise DeobfuscationFailError(
            'Bytes at index 73 is not header for bytes',
            severity='low',
            status='expected',
        )
    payload_len = int.from_bytes(header[2:][::-1])
    payload_start = 79
    payload_end = payload_start + payload_len
    payload = marshalled_bytes[payload_start:payload_end]
    trailer = marshalled_bytes[payload_end:payload_end + 2]
    if trailer != b'N)':
        raise DeobfuscationFailError(
            'Malformed marshal payload, length does not match trailer',
            severity='low',
            status='expected',
        )
    return payload


def regex_nab_bytes(marshalled_bytes: bytes) -> bytes:
    """
    Uses regex to grab the payload
    """
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
            raise DeobfuscationFailError(
                'Malformed marshal payload, length does not match trailer',
                severity='low',
                status='expected',
            )
        rtn_bytes.append(payload)
        current_idx = payload_start + payload_len + 2
    if len(rtn_bytes) > 1:
        raise DeobfuscationFailError(
            'Multiple payloads found in bytes',
            severity='low',
            status='expected',
        )
    return rtn_bytes[0]


def deobf_not_pyobfuscate(file: TextIO) -> bytes:
    """
    Deobfuscates the not pyobfuscate schema
    :return: Marshalled code object of the source code
    """
    obf_bytes = nab_surface_payload(file.read())
    while True:
        marshalled_bytes = deobf_obf(obf_bytes)
        try:
            obf_bytes = nab_bytes(marshalled_bytes)
        except DeobfuscationFailError:
            return marshalled_bytes
        if not obf_bytes:
            return marshalled_bytes


def format_not_pyobfuscate(marshalled_bytes: bytes) -> str:
    webhooks = BYTES_WEBHOOK_REGEX.findall(marshalled_bytes)
    rtn_string = StringIO()
    rtn_string.write(f'Marshalled bytes:\n{marshalled_bytes!r}\n')

    if webhooks:
        rtn_string.write('\nWebhooks found:\n')
        for webhook in webhooks:
            rtn_string.write(f'{webhook.decode()}\n')

    return rtn_string.getvalue()
