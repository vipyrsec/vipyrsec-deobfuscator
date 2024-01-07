import re
import base64
import ast


WEBHOOK_REGEX = re.compile(
    r'https?://(ptb\.|canary\.)?discord(app)?\.com/api(/v\d{1,2})?/webhooks/(\d{17,21})/([\w-]{68})'
)


def unwrap_base64_b64decode(inp_string):
    """
    Decodes a common pattern in lzma spam
    """
    return re.sub(
        r'getattr\(__import__\(bytes\(\[98, 97, 115, 101, 54, 52]\)\.decode\(\)\), '
        r'bytes\(\[98, 54, 52, 100, 101, 99, 111, 100, 101]\)'
        r'\.decode\(\)\)\(bytes\(\[(\d+(?:, \d+)*)]\)\)\.decode\(\)',
        lambda s: f"'{base64.b64decode(bytes(map(int, s.group(1).split(', ')))).decode()}'",
        inp_string
    )
