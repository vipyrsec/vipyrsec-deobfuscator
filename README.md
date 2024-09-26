# vipyrsec-deobfuscator

## Installation

```bash
# Without argcomplete support
pip install git+https://github.com/vipyrsec/vipyrsec-deobfuscator.git
# With argcomplete support
pip install "vipyr-deobf[argcomplete] @ git+https://github.com/vipyrsec/vipyrsec-deobfuscator.git"
```

## Supported Obfuscation Types

- Vare
- FCT (FreeCodingTools)
- BlankOBF v2
- Hyperion (Incomplete)
- PyObfuscate

## Usage

```bash
py -m vipyr-deobf mal.py
```

By default, the deobfuscator will make a 'best attempt' at discerning the obfuscation. If it is unable to detect the obfuscation type,
one can be manually supplied with the `-t` or `--type` switch.

Multiple obfuscation types and versions can be provided, separated by a comma. For example, `vipyr-deobf mal.py -t foov1,foov2,bar` will run the deobfuscator with version 1, 2 of `foo` and version 1 of `bar`.

The deobfuscator also supports writing an output to a file with the `-o` or `--output` switch.

## Adding Deobfuscators

If you want to add your own deobfuscators, you can simply add a file to the `deobfuscators` folder and `vipyr-deobf` will detect it
automatically. 

The format is `**/deobfuscators/DeobfName/deobfname.py`. `deobfname` should equal `DeobfName` with all characters lowercased
and spaces removed, and versioning is also supported by adding `_v(version number)` to the file name (if not provided, version defaults to 1). 
For example,
```
Foo/foo_v1.py
Eggs Bacon/eggsbacon_v2.py
Eggs Bacon/eggsbacon.py
```
are all valid, but
```
Foo/bar.py (different file name)
Foo/barv1.py (no _ before v)
```
are not.

After you've added your code to the file, add the following lines:
```py
from vipyr_deobf.deobf_base import Deobfuscator, register

blankobf_v2_deobf = Deobfuscator(deobf, format_results, scan)
register(blankobf_v2_deobf)
```
Look at the type hints for the `Deobfuscator` class to determine what the three functions
should look like and wrap your code into those three functions.