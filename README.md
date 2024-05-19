# vipyrsec-deobfuscator

## Installation

```bash
pip install git+https://github.com/vipyrsec/vipyrsec-deobfuscator.git
```

## Supported Obfuscation Types

- Vare
- FreeCodingTools
- BlankOBF v2
- Hyperion (Incomplete)

## Usage

```bash
py -m vipyrsec-deobf mal.py
```

By default, the deobfuscator will make a 'best attempt' at discerning the obfuscation. If it is unable to detect the obfuscation type
one can be manually supplied with the `-t` or `--type` switch.

The deobfuscator also supports writing an output to a file with the `-o` or `--output` switch.
