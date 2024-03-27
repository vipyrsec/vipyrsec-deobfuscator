import re

VARE_NAME_REGEX = re.compile(r'__VareObfuscator__')
SAINT_REGEX = re.compile(r'def saint\d+\(\):')
MIKEY_REGEX = re.compile(r'__mikey__')


def scan_vare(code: str):
    return any(
        pattern.search(code)
        for pattern in (
            VARE_NAME_REGEX,
            SAINT_REGEX,
            MIKEY_REGEX,
        )
    )
