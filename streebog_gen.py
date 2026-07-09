import gostcrypto.gosthash as g
PV = "/mnt/c/Users/jeff/Documents/autoresearch/pv"
def sb(algo, data):
    h = g.new(algo); h.update(data)
    return bytes.fromhex(h.hexdigest())[::-1].hex()   # hashcat stores Streebog digests byte-reversed
# validate the pure-Python reference against hashcat's own known vectors
V = {"streebog256": "57e9e50caec93d72e9498c211d6dc4f4d328248b48ecf46ba7abfa874f666e36",
     "streebog512": "5d5bdba48c8f89ee6c0a0e11023540424283e84902de08013aeeb626e819950bb32842903593a1d2e8f71897ff7fe72e17ac9ba8ce1d1d2f7e9c4359ea63bdc3"}
for a, v in V.items():
    got = sb(a, b"hashcat")
    assert got == v, f"{a} impl mismatch: {got} != {v}"
print("gostcrypto validated against hashcat Streebog-256/512 vectors")
# fixed 4-char lowercase passwords so one -a 3 mask ?l?l?l?l covers them all
pws = ["abcd", "word", "test", "gost", "hash", "pass", "mask", "frub"]
for mode, algo in [("11700", "streebog256"), ("11800", "streebog512")]:
    with open(f"{PV}/sb_h_{mode}.txt", "w") as hf:
        for p in pws: hf.write(sb(algo, p.encode()) + "\n")
print("generated", len(pws), "reference hashes each for 11700/11800")
