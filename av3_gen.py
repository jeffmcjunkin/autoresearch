import hashlib
from Crypto.Hash import keccak
import gostcrypto.gosthash as gost
PV = "/mnt/c/Users/jeff/Documents/autoresearch/pv"

def sha3(bits): return lambda d: getattr(hashlib, f"sha3_{bits}")(d).hexdigest()
def kec(bits):  return lambda d: keccak.new(digest_bits=bits, data=d).hexdigest()
def sm3(d):     return hashlib.new("sm3", d).hexdigest()   # OpenSSL SM3
def sb(name):
    def f(d):
        h = gost.new(name); h.update(d)
        return bytes.fromhex(h.hexdigest())[::-1].hex()   # hashcat stores Streebog byte-reversed
    return f

# mode -> (independent reference fn, hashcat ST_HASH("hashcat") for self-validation)
REF = {
 "17300": (sha3(224), "412ef78534ba6ab0e9b1607d3e9767a25c1ea9d5e83176b4c2817a6c"),
 "17400": (sha3(256), "d60fcf6585da4e17224f58858970f0ed5ab042c3916b76b0b828e62eaf636cbd"),
 "17500": (sha3(384), "983ba28532cc6320d04f20fa485bcedb38bddb666eca5f1e5aa279ff1c6244fe5f83cf4bbf05b95ff378dd2353617221"),
 "17600": (sha3(512), "7c2dc1d743735d4e069f3bda85b1b7e9172033dfdd8cd599ca094ef8570f3930c3f2c0b7afc8d6152ce4eaad6057a2ff22e71934b3a3dd0fb55a7fc84a53144e"),
 "17700": (kec(224),  "e1dfad9bafeae6ef15f5bbb16cf4c26f09f5f1e7870581962fc84636"),
 "17800": (kec(256),  "203f88777f18bb4ee1226627b547808f38d90d3e106262b5de9ca943b57137b6"),
 "17900": (kec(384),  "5804b7ada5806ba79540100e9a7ef493654ff2a21d94d4f2ce4bf69abda5d94bf03701fe9525a15dfdc625bfbd769701"),
 "18000": (kec(512),  "2fbf5c9080f0a704de2e915ba8fdae6ab00bbc026b2c1c8fa07da1239381c6b7f4dfd399bf9652500da723694a4c719587dd0219cb30eabe61210a8ae4dc0b03"),
 "31100": (sm3,       "51227e48ea74827b77fc142c3ec21d25cc42c794e6ac422825cd47ad4ac7913d"),
 "11700": (sb("streebog256"), "57e9e50caec93d72e9498c211d6dc4f4d328248b48ecf46ba7abfa874f666e36"),
 "11800": (sb("streebog512"), "5d5bdba48c8f89ee6c0a0e11023540424283e84902de08013aeeb626e819950bb32842903593a1d2e8f71897ff7fe72e17ac9ba8ce1d1d2f7e9c4359ea63bdc3"),
}
pws = ["abcd", "word", "test", "hash", "pass", "mask", "gost", "frub"]   # 4-char lowercase -> mask ?l?l?l?l
ok, bad = [], []
for m, (fn, st) in REF.items():
    try:
        got = fn(b"hashcat")
        assert got == st, f"reference != hashcat ST_HASH ({got[:16]}..)"
        with open(f"{PV}/av3_h_{m}.txt", "w") as hf:
            for p in pws: hf.write(fn(p.encode()) + "\n")
        ok.append(m)
    except Exception as e:
        bad.append(f"{m}({e})")
print("validated+generated:", " ".join(ok))
if bad: print("SKIPPED:", " ".join(bad))
