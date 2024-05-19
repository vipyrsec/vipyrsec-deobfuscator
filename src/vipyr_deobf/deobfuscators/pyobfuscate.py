import ast
import base64
import hashlib
import logging
from ast import Assign, Attribute, Call, Constant, Dict, Lambda, Name, keyword

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from ..utils import WEBHOOK_REGEX

logger = logging.getLogger('deobf')


class PayloadExtractor(ast.NodeVisitor):
    def __init__(self):
        self.obf_type = None
        self.payload = None

    def visit_Assign(self, node):
        match node:
            case Assign(
                targets=[Name(id='pyobfuscate' as obf_type)],
                value=Call(
                    func=Lambda(),
                    keywords=[
                        keyword(
                            value=Dict(
                                keys=[
                                    Constant(value=str(payload_00)),
                                    Constant(value='exec'),
                                    Constant(value='eval'),
                                ],
                                values=[
                                    Constant(value=str(payload_10)),
                                    Constant(value=str()),
                                    Call(
                                        func=Attribute(
                                            value=Name(id='bytes'),
                                            attr='fromhex',
                                        ),
                                        args=[
                                            Call(
                                                func=Attribute(
                                                    value=Constant(value=str(payload_12)),
                                                    attr='replace',
                                                ),
                                                args=[
                                                    Constant(value='\n'),
                                                    Constant(value=''),
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        )
                    ]
                )
            ):
                self.obf_type = obf_type
                self.payload = (payload_00, payload_10, bytes.fromhex(payload_12.replace('\n', '')))
            case Assign(
                targets=[Name(id='obfuscate' as obf_type)],
                value=Dict(
                    keys=[Constant(value=key)],
                    values=[Constant(value=value)],
                )
            ):
                self.obf_type = obf_type
                self.payload = (key, value)


PayloadType1 = tuple[str, str, bytes]
PayloadType2 = tuple[str, str]


def extract_payload(tree: ast.Module) -> None | tuple[str, PayloadType1 | PayloadType2]:
    extractor = PayloadExtractor()
    extractor.visit(tree)
    if not extractor.obf_type:
        logger.error('Payload not found')
        return None
    return extractor.obf_type, extractor.payload


def deobf_pyobfuscate(code: str) -> str | None:
    logger.info('Running pyobfuscate')
    tree = ast.parse(code)
    result = extract_payload(tree)
    if result is None:
        return None

    logger.info('Payload found')
    obf_type, payload = result
    if obf_type == 'pyobfuscate':
        logger.info('Payload identified as first variant')
        return deobf_first_variant(*payload)
    elif obf_type == 'obfuscate':
        logger.info('Payload identified as second variant')
        return deobf_second_variant(*payload)
    else:
        logger.error('Unknown obf type. This should never happen, so please report this.')


def deobf_first_variant(key0: str, value0: str, value2: bytes) -> str:
    logger.info('Running first variant on payload')
    key = hashlib.sha256(f'{key0}{value0}'.encode()).digest()[:24]
    try:
        logger.info('Trying first type of first variant')
        return first_variant_decoder(key, value2)
    except ValueError:
        logger.info('Payload appears to be second type of first variant')
    logger.info('Trying second type of first variant')
    key = hashlib.sha256(f'{key0}{value0[:-1]}'.encode()).digest()[:24]
    return first_variant_decoder(key, value2)


def first_variant_decoder(key: bytes, data: bytes) -> str:
    cipher = AES.new(key, AES.MODE_CBC, data[:AES.block_size])
    decrypted_data = cipher.decrypt(data[AES.block_size:])
    return unpad(decrypted_data, AES.block_size).decode()


def deobf_second_variant(value: str, key: str) -> str:
    logger.info('Running second variant on payload')
    key = base64.b85decode(key)
    value = value[1:-1]
    dk = hashlib.pbkdf2_hmac('sha256', value.encode(), key[:8], 100000)
    cipherkey, data = dk[:16], dk[16:]
    return AES.new(cipherkey, AES.MODE_CFB, data).decrypt(key[8:]).decode()


def format_pyobfuscate(deobfed_code: str) -> str:
    logger.info('Code has been deobfuscated successfully')
    webhooks = WEBHOOK_REGEX.findall(deobfed_code)
    if webhooks:
        logger.info('Webhooks found:')
        for webhook in webhooks:
            logger.info(f'{webhook}')
    return deobfed_code
