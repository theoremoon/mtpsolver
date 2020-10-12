from binascii import unhexlify
import collections
import string
import tempfile
import os
import subprocess
import sys


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for (x, y) in zip(a, b))


ciphers = []
with open(sys.argv[1], "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        ciphers.append(unhexlify(line))

key = [0] * max(len(x) for x in ciphers)

for i, ct in enumerate(ciphers):
    counter = collections.Counter()
    for j, ct2 in enumerate(ciphers):
        if i == j:
            continue
        for p, b in enumerate(xor(ct, ct2)):
            c = chr(b)
            if c in string.printable and c.isalpha():
                counter[p] += 1
    space_index = []
    for p, cnt in counter.items():
        if cnt >= len(ciphers) * 0.6:
            space_index.append(p)

    xor_with_space = xor(ct, bytes(0x20 for _ in range(len(ct))))
    for index in space_index:
        key[index] = xor_with_space[index]

def encode(p):
    return "".join(chr(b) if key[i] and b != 0x0a and b != 0x0d  else "*" for i, b in enumerate(p))

fd, name = tempfile.mkstemp()
while True:
    plaintexts = []
    for c in ciphers:
        plaintext = xor(c, bytes(key))
        plaintexts.append(
            encode(plaintext)
        )

    with open(name, "w") as f:
        for p in plaintexts:
            f.write(p)
            f.write("\n")
    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, name])

    with open(name, "r") as f:
        lines = f.readlines()

    changed = False
    for i in range(min(len(plaintexts), len(lines))):
        for j in range(min(len(plaintexts[i]), len(lines[i]))):
            if plaintexts[i][j] != lines[i][j]:
                key[j] = ciphers[i][j] ^ ord(lines[i][j])
                changed = True
    if not changed:
        break

for c in ciphers:
    plaintext = xor(c, bytes(key))
    print(encode(plaintext))
