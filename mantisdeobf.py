from hyperion import hyperion_deobf
from lzmaspam import lzma_b64_deobf

import argparse

supported_obfuscations = ['hyperion', 'lzmaspam']


def run():
    parser = argparse.ArgumentParser(
        prog='Mantis Deobfuscator',
        description='Deobfuscates Obfuscated Scripts'
    )
    parser.add_argument('-p', '--path')
    parser.add_argument('-t', '--type')
    args = parser.parse_args()
    while True:
        if args.type in supported_obfuscations:
            with open(args.path) as file:
                if args.type == 'hyperion':
                    hyperion_deobf(file)
                    break
                elif args.type == 'lzmaspam':
                    lzma_b64_deobf(file)
                    break
        else:
            print('Unsupported obfuscation schema.')
            print('Supported obfuscations schemes include:')
            print(*supported_obfuscations, sep=", ")


if __name__ == '__main__':
    run()
