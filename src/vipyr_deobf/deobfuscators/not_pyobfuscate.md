# Name
- We do not know which obfuscator this format originates from, however it is picked up by our malware scanners as a product of pyobfuscate. As far as we know, this obfuscation format is not available in pyobfuscate, and so we have temporarily named it "not pyobfuscate", to distinguish it from the actual pyobfuscate products. Name suggestions are welcome.

# Obfuscation Format
- This flavour of obfuscation uses a function we will call `obf`, which we will define below:
```py
import base64
import zlib

def obf(inp: bytes) -> bytes:
    return zlib.compress(base64.b64encode(inp))[::-1]
```
- The source code is then obfuscated as follows:
1. Compile the code with `compile`.
2. Marshal the resulting code object with `marshal.dumps`.
3. Apply `obf`.
4. Repeat steps 1-3 some number of times.

# Usage
- As we do not currently have the ability to unmarshal full code objects, the output will (hopefully) be a marshalled code object containing the source code.
- The analyst will be able to analyze the resultant code for any important strings. A quick discord webhook search will also be applied.

# Internals
- The starting bytestring is given in raw text.
- `obf` is trivial to deobfuscate.
- To find the next layer in the bytes containing the marshalled code object, we try two methods:
1. It appears that the header for the payload in subsequent bytes always appear at index 73, so we check that the header and trailer are there and the length matches, and then grab the contents.
2. If step one didn't work, we use regex to look for a header, check the length and the trailer, and then grab the contents. If multiple or no payloads are found/payloads are malformed, then we assume we've reached the source code and output the contents to the analyst.
- We repeat this process until we've reached the source code.