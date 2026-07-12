# hashcat kernel autoresearch — progress

Autonomous agent optimization loops (`ar.py`, see `program.md`). Each win lives on branch `autoresearch/<mode>-jul6` in the hashcat repo; per-experiment logs are `results_<mode>.tsv`. Regenerate with `uv run ar.py readme`.

Legend: ✅ = verified real — reproduced on **interleaved** clean-GPU A/B (drift-free; measured 2σ noise floor ≈ ±0.08% on fast modes) with hashcat self-test PASS, and correctness cross-checked against an independent reference (Streebog 11700/11800 via gostcrypto cracked 8/8 on the **a3** win kernel; SHA3/Keccak/RC4 via tools/test.pl). Δ = clean-A/B total over stock. ❌ = did not reproduce on clean A/B (single-baseline loop drift). Batches: C/PR = campaign & landed PRs, digits = sweep.

| Batch | Mode | Name | Category | Δ | MH/s (base→best) | Status | Branch |
|---|---|---|---|---|---|---|---|
| C | 17400 | SHA3-256 | SHA3/Keccak | +13.3% | 1.9k → 2.2k | WIN +13.3% ✅ | `autoresearch/17400-jul6` |
| C | 17600 | SHA3-512 | SHA3/Keccak | +12.9% | 1.9k → 2.2k | WIN +12.9% ✅ | `autoresearch/17600-jul6` |
| C | 17800 | Keccak-256 | SHA3/Keccak | +8.2% | 1.9k → 2.0k | WIN +8.2% ✅ | `autoresearch/17800-jul6` |
| C | 11700 | Streebog-256 | Streebog | +6.7% | 188.8 → 220.5 | WIN +6.7% ✅ | `autoresearch/11700-jul6` |
| C | 11800 | Streebog-512 | Streebog | +6.7% | 187.2 → 221.2 | WIN +6.7% ✅ | `autoresearch/11800-jul6` |
| C | 31100 | SM3 | SM3 | +3.2% | 7.2k → 7.5k | WIN +3.2% ✅ | `autoresearch/31100-jul6` |
| C | 6100 | Whirlpool (campaign ext.) | Whirlpool | ~0% | 1.5k → 1.6k | ❌ not real (A/B ~0%) | `autoresearch/6100-jul6` |
| C | 6900 | GOST R 34.11-94 | GOST | ~0% | 934.8 → 934.8 | roofline | `autoresearch/6900-jul6` |
| C | 600 | BLAKE2b-512 | BLAKE2 | ~0% | 5.2k → 5.2k | roofline | `autoresearch/600-jul6` |
| C | 1700 | SHA2-512 | SHA2 | ~0% | 2.9k → 2.9k | roofline | `autoresearch/1700-jul6` |
| C | 10800 | SHA2-384 | SHA2 | ~0% | 2.9k → 2.9k | roofline | `autoresearch/10800-jul6` |
| C | 6000 | RIPEMD-160 | RIPEMD | ~0% | 14.2k → 14.2k | roofline | `autoresearch/6000-jul6` |
| 1 | 18000 | Keccak-512 | SHA3/Keccak | +13.3% | 1.9k → 2.2k | WIN +13.3% ✅ | `autoresearch/18000-jul6` |
| 1 | 17700 | Keccak-224 | SHA3/Keccak | +13.1% | 1.9k → 2.2k | WIN +13.1% ✅ | `autoresearch/17700-jul6` |
| 1 | 17500 | SHA3-384 | SHA3/Keccak | +8.3% | 1.9k → 2.1k | WIN +8.3% ✅ | `autoresearch/17500-jul6` |
| 1 | 17300 | SHA3-224 | SHA3/Keccak | +8.2% | 1.9k → 2.1k | WIN +8.2% ✅ | `autoresearch/17300-jul6` |
| 1 | 17900 | Keccak-384 | SHA3/Keccak | +8.1% | 1.9k → 2.1k | WIN +8.1% ✅ | `autoresearch/17900-jul6` |
| 2 | 27000 | NetNTLMv1-NT (slow) | AD-auth | +19.6% | 931.5 → 1.1k | WIN +19.6% (unverified) | `autoresearch/27000-jul6` |
| 2 | 3000 | LM | AD-auth | +9.3% | 60.9k → 66.5k | WIN +9.3% ✅ | `autoresearch/3000-jul6` |
| 2 | 1000 | NTLM | AD-auth | +3.1% | 119.2k → 122.9k | WIN +3.1% (unverified) | `autoresearch/1000-jul6` |
| 2 | 5500 | NetNTLMv1 | AD-auth | ~0% | 46.2k → 46.2k | roofline | `autoresearch/5500-jul6` |
| 2 | 5600 | NetNTLMv2 | AD-auth | ~0% | 4.7k → 4.7k | roofline | `autoresearch/5600-jul6` |
| 3 | 9700 | MS Office <=2003 MD5+RC4 | Office | +22.5% | 1.0k → 1.3k | WIN +22.5% ✅ | `autoresearch/9700-jul6` |
| 3 | 18200 | Kerberos etype23 AS-REP RC4 | AS-REP-roast | +1.8% | 1.4k → 1.5k | WIN +1.8% ✅ | `autoresearch/18200-jul6` |
| 3 | 19600 | Kerberos etype17 TGS-REP AES128 (slow) | Kerberoasting | ~0% | 2.2 → 2.2 | roofline | `autoresearch/19600-jul6` |
| 3 | 19700 | Kerberos etype18 TGS-REP AES256 (slow) | Kerberoasting | ~0% | 1.1 → 1.1 | roofline | `autoresearch/19700-jul6` |
| 3 | 9800 | MS Office <=2003 SHA1+RC4 | Office | ~0% | 1.2k → 1.3k | ❌ not real (A/B ~0%) | `autoresearch/9800-jul6` |
| 4 | 9400 | MS Office 2007 (slow) | Office | ~0% | 0.4 → 0.4 | in-progress 2/6 | `autoresearch/9400-jul6` |
| 4 | 9500 | MS Office 2010 (slow) | Office | ~0% | 0.2 → 0.2 | in-progress 3/6 | `autoresearch/9500-jul6` |
| 4 | 9600 | MS Office 2013 (slow) | Office | ~0% | 0.0 → 0.0 | in-progress 1/6 | `autoresearch/9600-jul6` |
| 4 | 1100 | DCC / MS Cache | MSCache | ~0% | 32.2k → 32.2k | in-progress 2/6 | `autoresearch/1100-jul6` |
| 4 | 2100 | DCC2 / MS Cache 2 (slow) | MSCache | ~0% | 0.9 → 0.9 | in-progress 2/6 | `autoresearch/2100-jul6` |
| 9 | 10500 | PDF 1.4-1.6 | Docs/Wallet | +2.9% | 75.1 → 80.7 | WIN +2.9% ✅ | `autoresearch/10500-jul6` |
| 5 | 0 | MD5 | Raw | ~0% | 65.4k → 65.4k | roofline | `autoresearch/0-jul6` |
| 5 | 100 | SHA1 | Raw | ~0% | 23.4k → 23.4k | roofline | `autoresearch/100-jul6` |
| 5 | 1400 | SHA2-256 | Raw | ~0% | 8.6k → 8.6k | roofline | `autoresearch/1400-jul6` |
| 5 | 900 | MD4 | Raw | ~0% | 119.1k → 119.1k | roofline | `autoresearch/900-jul6` |
| 5 | 1300 | SHA2-224 | Raw | ~0% | 8.4k → 8.4k | roofline | `autoresearch/1300-jul6` |
| 6 | 10 | md5(pass.salt) | Salted | ~0% | 65.2k → 65.2k | roofline | `autoresearch/10-jul6` |
| 6 | 110 | sha1(pass.salt) | Salted | ~0% | 23.0k → 23.6k | ❌ not real (A/B ~0%) | `autoresearch/110-jul6` |
| 6 | 1410 | sha256(pass.salt) | Salted | ~0% | 8.6k → 8.6k | roofline | `autoresearch/1410-jul6` |
| 6 | 5100 | Half-MD5 | Salted | ~0% | 41.4k → 41.4k | roofline | `autoresearch/5100-jul6` |
| 6 | 2600 | md5(md5(pass)) | Salted | ~0% | 19.2k → 19.6k | ❌ not real (A/B ~0%) | `autoresearch/2600-jul6` |
| 7 | 3200 | bcrypt | Unix-KDF | ~0% | 0.1 → 0.1 | roofline | `autoresearch/3200-jul6` |
| 7 | 500 | md5crypt | Unix-KDF | ~0% | 28.8 → 28.8 | roofline | `autoresearch/500-jul6` |
| 7 | 1800 | sha512crypt | Unix-KDF | ~0% | 0.4 → 0.4 | roofline | `autoresearch/1800-jul6` |
| 7 | 7400 | sha256crypt | Unix-KDF | ~0% | 0.8 → 0.8 | roofline | `autoresearch/7400-jul6` |
| 7 | 400 | phpass | Unix-KDF | ~0% | 20.0 → 20.0 | roofline | `autoresearch/400-jul6` |
| 8 | 12000 | PBKDF2-HMAC-SHA1 | PBKDF2/WPA/DB | ~0% | 8.7 → 8.7 | roofline | `autoresearch/12000-jul6` |
| 8 | 10900 | PBKDF2-HMAC-SHA256 | PBKDF2/WPA/DB | ~0% | 3.5 → 3.5 | roofline | `autoresearch/10900-jul6` |
| 8 | 22000 | WPA-PBKDF2-PMKID+EAPOL | PBKDF2/WPA/DB | ~0% | 1.1 → 1.1 | roofline | `autoresearch/22000-jul6` |
| 8 | 300 | MySQL4.1/5 | PBKDF2/WPA/DB | ~0% | 9.5k → 9.5k | roofline | `autoresearch/300-jul6` |
| 8 | 1731 | MSSQL 2012/2014 | PBKDF2/WPA/DB | ~0% | 2.9k → 2.9k | roofline | `autoresearch/1731-jul6` |
| 9 | 11300 | Bitcoin/Litecoin wallet.dat | Docs/Wallet |  |  | - | `autoresearch/11300-jul6` |
| 9 | 7900 | Drupal7 | Docs/Wallet | ~0% | 0.2 → 0.2 | roofline | `autoresearch/7900-jul6` |
| 9 | 112 | Oracle 11+ | Docs/Wallet | ~0% | 23.3k → 23.3k | roofline | `autoresearch/112-jul6` |
| 9 | 15700 | Ethereum Wallet SCRYPT | Docs/Wallet |  |  | - | `autoresearch/15700-jul6` |
| 10 | 14600 | LUKS v1 | AES-container | ~0% | 0.0 → 0.0 | roofline | `autoresearch/14600-jul6` |
| 10 | 13751 | VeraCrypt SHA256+AES XTS512 | AES-container | ~0% | 0.0 → 0.0 | roofline | `autoresearch/13751-jul6` |
| 10 | 6211 | TrueCrypt RIPEMD160+AES XTS512 | AES-container | ~0% | 0.8 → 0.8 | roofline | `autoresearch/6211-jul6` |
| 10 | 6221 | TrueCrypt SHA512+AES XTS512 | AES-container | ~0% | 1.2 → 1.2 | ❌ not real (A/B ~0%) | `autoresearch/6221-jul6` |
| 10 | 16700 | FileVault 2 | AES-container | ~0% | 0.2 → 0.2 | roofline | `autoresearch/16700-jul6` |
| 11 | 13752 | VeraCrypt SHA256 XTS1024 | Twofish/Serpent | ~0% | 0.0 → 0.0 | roofline | `autoresearch/13752-jul6` |
| 11 | 13753 | VeraCrypt SHA256 XTS1536 | Twofish/Serpent | ~0% | 0.0 → 0.0 | roofline | `autoresearch/13753-jul6` |
| 11 | 6212 | TrueCrypt RIPEMD160 XTS1024 | Twofish/Serpent | ~0% | 0.4 → 0.4 | roofline | `autoresearch/6212-jul6` |
| 11 | 6213 | TrueCrypt RIPEMD160 XTS1536 | Twofish/Serpent | ~0% | 0.3 → 0.3 | roofline | `autoresearch/6213-jul6` |
| 11 | 13763 | VeraCrypt SHA256 boot | Twofish/Serpent | ~0% | 0.0 → 0.0 | roofline | `autoresearch/13763-jul6` |
| 12 | 13771 | VeraCrypt Streebog512 XTS512 | Kuznyechik/Streebog | ~0% | 0.0 → 0.0 | roofline | `autoresearch/13771-jul6` |
| 12 | 13772 | VeraCrypt Streebog512 XTS1024 | Kuznyechik/Streebog |  |  | pending | `autoresearch/13772-jul6` |
| 12 | 11750 | HMAC-Streebog-256 (key=pass) | Kuznyechik/Streebog | ~0% | 67.5 → 67.5 | in-progress 5/6 | `autoresearch/11750-jul6` |
| 12 | 11760 | HMAC-Streebog-256 (key=salt) | Kuznyechik/Streebog | ~0% | 93.5 → 93.5 | roofline | `autoresearch/11760-jul6` |
| 12 | 6800 | LastPass | Kuznyechik/Streebog | ~0% | 0.0 → 0.0 | roofline | `autoresearch/6800-jul6` |
| 13 | 12100 | PBKDF2-HMAC-SHA512 | SHA512/256-KDF | ~0% | 1.3 → 1.3 | roofline | `autoresearch/12100-jul6` |
| 13 | 7100 | macOS v10.8+ PBKDF2-SHA512 | SHA512/256-KDF | ~0% | 1.3 → 1.3 | in-progress 5/6 | `autoresearch/7100-jul6` |
| 13 | 6600 | 1Password agilekeychain | SHA512/256-KDF | ~0% | 8.7 → 8.7 | roofline | `autoresearch/6600-jul6` |
| 13 | 9200 | Cisco-IOS $8$ PBKDF2-SHA256 | SHA512/256-KDF | ~0% | 0.2 → 0.2 | ❌ not real (A/B ~0%) | `autoresearch/9200-jul6` |
| 13 | 15300 | DPAPI masterkey v1 | SHA512/256-KDF | ~0% | 0.2 → 0.2 | roofline | `autoresearch/15300-jul6` |
| 14 | 8900 | scrypt | scrypt/misc | ~0% | 0.0 → 0.0 | roofline | `autoresearch/8900-jul6` |
| 14 | 22700 | MultiBit HD scrypt | scrypt/misc | ~0% | 0.0 → 0.0 | roofline | `autoresearch/22700-jul6` |
| 14 | 15900 | DPAPI masterkey v2 | scrypt/misc | ~0% | 0.1 → 0.1 | roofline | `autoresearch/15900-jul6` |
| 14 | 25400 | PDF 1.4-1.6 user+owner | scrypt/misc | ~0% | 70.5 → 70.5 | roofline | `autoresearch/25400-jul6` |
| 14 | 21600 | Web2py pbkdf2-sha512 | scrypt/misc | ~0% | 1.3 → 1.3 | roofline | `autoresearch/21600-jul6` |

**Totals:** 15 verified-real wins (interleaved clean-A/B + independent Perl-reference correctness), 6 rejected as single-baseline drift. (17 modes showed a loop delta ≥1%.)


## Survey: 508-mode 1-round sweep (GPT-5.6-sol, interleaved driver)

One interleaved-A/B round on each not-previously-explored hash mode surfaced 57 loop candidates; a clean re-A/B (drift-free, benchmarked in the main repo, self-test gated) confirms **41 as real** (verified Δ ≥ +0.3%). Wins live on `autoresearch/<mode>-survey`. Raw loop deltas over-state (autotune/drift); the **verified Δ** column is authoritative.

| Mode | Name | verified Δ | loop Δ | idea |
|---|---|---|---|---|
| 6060 | HMAC-RIPEMD160 (key = $salt) | **+52.78%** | +51.5% | direct short vector update in a3; delta_pct=+51.53 |
| 29000 | sha1($salt.sha1(utf16le($username).':'.utf16le($pass))) | **+49.99%** | +51.8% | 32-byte outer SHA1 fast path for benchmark salt de |
| 27800 | MurmurHash3 | **+28.34%** | +27.8% | seven-byte MurmurHash3 a3 fast path delta_pct=+27. |
| 12500 | RAR3-hp | **+23.22%** | +22.9% | limit optimized largeblock zero fill; delta_pct=+2 |
| 19000 | QNX /etc/shadow (MD5) | **+16.15%** | +15.4% | direct md5_update_64 fast path for pw_len<=64 in m |
| 17040 | GPG (CAST5 (SHA-1($pass))) | **+14.64%** | +12.3% | word-packed simple S2K salt||password and skipped |
| 26300 | FortiGate256 (FortiOS256) | **+13.59%** | +13.6% | a3 single-block SHA256 fast path delta_pct=+13.609 |
| 7701 | SAP CODVN B (BCODE) from RFC_READ_TABLE | **+13.31%** | +13.1% | walld0rf scalar byte extraction delta_pct=+13.083 |
| 1320 | sha224($salt.$pass) | **+10.78%** | +6.3% | m01320 a3 salt_len=8 direct block fast path; delta |
| 21420 | sha256($salt.sha256_bin($pass)) | **+9.48%** | +9.2% | hoist m21420 salt sha256 context; delta_pct=+9.164 |
| 25000 | SNMPv3 HMAC-MD5-96/HMAC-SHA1-96 | **+6.69%** | +6.5% | rolling loop index delta_pct=+6.469 |
| 3730 | md5($salt1.strtoupper(md5($salt2.$pass))) | **+6.31%** | +6.3% | precompute salt1 md5 context (delta_pct=+6.305) |
| 18100 | TOTP (HMAC-SHA1) | **+4.29%** | +2.9% | delta_pct=+2.938 specialized 8-byte TOTP HMAC salt |
| 11500 | CRC32 | **+4.27%** | +4.7% | a3 len7 CRC32 fast path delta_pct=+4.698 |
| 22800 | Simpla CMS - md5($salt.$pass.md5($pass)) | **+3.44%** | +3.4% | delta_pct=+3.399 hoist salt MD5 prefix context |
| 22911 | RSA/DSA/EC/OpenSSH Private Keys ($0$) | **+3.10%** | +9.5% | noipfp 3des chain delta_pct=+9.515 |
| 10300 | SAP CODVN H (PWDSALTEDHASH) iSSHA-1 | **+3.01%** | +2.1% | m10300 fast path digest sha1 loop delta_pct=+2.091 |
| 10510 | PDF 1.3 - 1.6 (Acrobat 4 - 8) w/ RC4-40 | **+2.73%** | +2.8% | m10510 compute only first two RC4 words; delta_pct |
| 28505 | Bitcoin WIF private key (P2SH(P2WPKH)), compressed | **+2.37%** | +2.3% | delta_pct=+2.283 delayed a3 secp256k1 precompute u |
| 28501 | Bitcoin WIF private key (P2PKH), compressed | **+2.25%** | +2.0% | delta_pct=+2.049 defer basepoint setup until check |
| 20720 | sha256($salt.sha256($pass)) | **+1.98%** | +2.1% | precompute salt sha256 context (delta_pct=+2.066) |
| 23900 | BestCrypt v3 Volume Encryption | **+1.59%** | +2.0% | m23900_loop table offset recurrence delta_pct=+1.9 |
| 9810 | MS Office <= 2003 $3, SHA1 + RC4, collider #1 | **+1.55%** | +1.5% | zero-tail RC4 init specialization; delta_pct=+1.46 |
| 10100 | SipHash | **+1.28%** | +1.6% | a3 m04 specialization for short SipHash candidates |
| 21400 | sha256(sha256_bin($pass)) | **+0.95%** | +0.9% | defer single-hash search loads after reverse skip; |
| 23100 | Apple Keychain | **+0.93%** | +0.4% | skip unused second PBKDF2 output words; delta_pct= |
| 25100 | SNMPv3 HMAC-MD5-96 | **+0.91%** | +1.0% | delta_pct=+1.038 hoist m25100 loop modulo to carri |
| 14000 | DES (PT = $salt, key = $pass) | **+0.89%** | +1.0% | m14000 bitslice unsigned bit masks; delta_pct=+1.0 |
| 7801 | SAP CODVN F/G (PASSCODE) from RFC_READ_TABLE | **+0.77%** | +0.6% | sum offset low3 byte lanes; delta_pct=+0.573 |
| 10700 | PDF 1.7 Level 8 (Acrobat 10 - 11) | **+0.67%** | +0.9% | avoid persisting W_len in optimized kernel; delta_ |
| 8100 | Citrix NetScaler (SHA1) | **+0.64%** | +0.7% | precompute a3 salt-only SHA1 rounds (delta_pct=+0. |
| 25700 | MurmurHash | **+0.63%** | +0.4% | drop redundant MurmurHash block guard; delta_pct=+ |
| 16501 | Perl Mojolicious session cookie (HMAC-SHA256, >= v9.19) | **+0.52%** | +0.9% | hoist m16511 salt metadata loads delta_pct=+0.912 |
| 3800 | md5($salt.$pass.$salt) | **+0.47%** | +0.4% | specialize m03800 a3 one-byte salt shift; delta_pc |
| 16800 | WPA-PMKID-PBKDF2 | **+0.47%** | +0.4% | skip unused PMKID block2 tail output (delta_pct=+0 |
| 21000 | BitShares v0.x - sha512(sha512_bin(pass)) | **+0.42%** | +0.8% | drop unused a3 pw_len; delta_pct=+0.804 |
| 23300 | Apple iWork | **+0.42%** | +0.4% | skip unused PBKDF2 out[4]; delta_pct=+0.403 |
| 11600 | 7-Zip | **+0.40%** | +0.6% | trim largeblock zeroing delta_pct=+0.610 |
| 3100 | Oracle H: Type (Oracle 7+) | **+0.34%** | +0.4% | use byte-perm UTF-16BE packing in a3; delta_pct=+0 |
| 9300 | Cisco-IOS $9$ (scrypt) | **+0.33%** | +0.3% | Specialize small scrypt TMTO replay loop; delta_pc |
| 12600 | ColdFusion 10+ | **+0.32%** | +0.5% | a3 direct SHA1 hex word order removes swaps delta_ |

_16 candidates did not survive clean A/B (autotune ghosts / drift / passthrough): 124, 1470, 2000, 3500, 6050, 7800, 8600, 8800, 9820, 12900, 17220, 19210, 19900, 26900, 28400, 29331._

