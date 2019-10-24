# Note: flag format is 'flag{...}'

from binascii import hexlify

xs = []
ct = open("out", "rb").read().strip().split(b"\n")[1]
for i in range(0, len(ct), 10):
    xs.append(hexlify(ct[i : i + 10]).decode())

print("\n".join(xs))
