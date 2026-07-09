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
