import base64
import zlib
import re
import ast
from pathlib import Path
import argparse


def extract_payload(filename: Path) -> str:
    bytes_regex = re.compile(r"\(b'.*'\)")
    with open(filename, 'r') as f:
        payload = f.read()
    return re.search(bytes_regex, payload)[0]


def prepare_layer(payload: str) -> str:
    return ast.literal_eval(payload)


def decode_layer(payload: str) -> str:
    reverse = payload[::-1]
    debase = base64.b64decode(reverse)
    decompress = zlib.decompress(debase)
    return decompress


def _get_payload_indices(marshalled_payload: bytes) -> bytes:
    magic_bytes = b"\x02\x73\x00\x00\x00\x00"
    magic_bytes_end = b"\x4e\x29"
    payload_index_starts = []
    payload_index_ends = []
    for i in range(len(marshalled_payload)):
        substring = marshalled_payload[i:i+len(magic_bytes)]
        if substring[0:1] == magic_bytes[0:1] and substring[-2:] == magic_bytes[-2:]:
            start_index = i+len(magic_bytes)
            payload_index_starts.append(start_index)
    for i in range(len(marshalled_payload)):
        substring = marshalled_payload[i:i+len(magic_bytes_end)]
        if substring == magic_bytes_end:
            payload_index_ends.append(i)
    return payload_index_starts, payload_index_ends


def _try_decode(marshalled_code: bytes, payload_starts: list, payload_ends: list) -> bytes:
    for starts in payload_starts:
        for ends in payload_ends:
            try:
                return decode_layer(marshalled_code[starts:ends])
            except: # Todo: Fix bare except with appropriate exception handling.
                print('Multiple valid substrings detected, trying next payload...')
                pass


def decode_layer_secondary(marshalled_payload: bytes) -> bytes:
    starts, ends =_get_payload_indices(marshalled_payload)
    return _try_decode(marshalled_payload, starts, ends)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog = 'Pyobfuscate Decoder',
        description = 'Attempts to decode PyObfuscate obfuscation.'
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    extracted_payload = extract_payload(args.filename)
    prepared_payload = prepare_layer(extracted_payload)
    decoded_layer = decode_layer(prepared_payload)
    while True:
        print(decoded_layer[0:200])
        user_in = input("Is this your code?(Y/N/Q) ")
        if user_in.upper() == 'Y':
            print(decoded_layer)
            break
        elif user_in.upper() == 'N':
            decoded_layer = decode_layer_secondary(decoded_layer)
        else:
            print("Goodbye.")
            break


if __name__ == '__main__':
    main()
