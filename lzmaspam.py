"""
Deobfuscator for an obfuscation schema that has heavy use of lzma.decompress and base64.b64decode
Example: https://hst.sh/raw/ojucipihoc
If the file begins with
    import base64
    import lzma
    exec(compile(lzma.decompress(base64.b64decode(...))))
Then it's likely this obfuscation schema
"""

import argparse
import ast
import base64
import codecs
import lzma
import re
from typing import NoReturn, TextIO


def lzma_b64_deobf(file: TextIO) -> re.Match:
    """
    Extracts webhook from code
    """
    code = lzma.decompress(
        ast.literal_eval(
            re.search(
                r"(b'.+?')\n",
                lzma.decompress(base64.b64decode(
                    ast.literal_eval(
                        re.search(r"b'.+?'", file.read()).group(0)
                    )
                )).decode()
            ).group(1)
        )
    ).decode()
    var_code, mal_code = re.split(r';(?=[^;]+$)', code)
    doggo = {k: v for k, v in re.findall(r'(_{3,})="(.+?)"(?:;|$)', var_code)}
    a, b, c, d = map(doggo.get, re.findall(r'_{3,}', mal_code))
    webhook = re.search(
        r'https://discord\.com/api/webhooks/[\w/]+',
        str(base64.b64decode(
            codecs.decode(a, 'rot13') + b + c[::-1] + d
        ))
    )
    return webhook


def run() -> NoReturn:
    parser = argparse.ArgumentParser(
        prog='LZMA Spam',
        description='Deobfuscates LZMASpam Obfuscated Scripts'
    )
    parser.add_argument('-p', '--path')
    args = parser.parse_args()
    try:
        with open(args.path, 'r') as file:
            webhook = lzma_b64_deobf(file)
    except Exception as e:
        print('This is probably a different obfuscation schema.')
        print('Exception: ', e)
    else:
        if webhook:
            print('Webhook:')
            print(webhook.group(0))
        else:
            print('No webhook found :(')


if __name__ == '__main__':
    run()
