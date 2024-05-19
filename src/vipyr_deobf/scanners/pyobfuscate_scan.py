import ast

from ..deobfuscators.pyobfuscate import PayloadExtractor


def scan_pyobfuscate(code: str):
    extractor = PayloadExtractor()
    extractor.visit(ast.parse(code))
    return bool(extractor.obf_type)
