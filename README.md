# hashcat kernel autoresearch — progress

Autonomous `claude -p` optimization loops (see `program.md`, `drive.sh`, `parallel.sh`). Each win lives on branch `autoresearch/<mode>-jul6` in the hashcat repo; per-experiment logs are `results_<mode>.tsv`. Regenerate this file with `bash gen_readme.sh`.

**Landed PRs** (already submitted, verified): RC4 S-box `KEY8` — [hashcat#4712](https://github.com/hashcat/hashcat/pull/4712) (+4.6% Kerberoasting, +8% Office, all RC4 modes); Whirlpool single-table — [hashcat#4713](https://github.com/hashcat/hashcat/pull/4713) (+7%).

Legend: ✅ = win verified on clean-GPU A/B + correctness; ❌ = win did not reproduce; batches C=first campaign, 1–4=current run.

| Batch | Mode | Name | Category | Δ | MH/s (base→best) | Status | Branch |
|---|---|---|---|---|---|---|---|
| C | 17600 | SHA3-512 | SHA3/Keccak | +13.4% | 1.9k → 2.2k | WIN +13.4% ✅ | `autoresearch/17600-jul6` |
| C | 17400 | SHA3-256 | SHA3/Keccak | +13.3% | 1.9k → 2.1k | WIN +13.3% ✅ | `autoresearch/17400-jul6` |
| C | 17800 | Keccak-256 | SHA3/Keccak | +8.2% | 1.9k → 2.0k | WIN +8.2% ✅ | `autoresearch/17800-jul6` |
| C | 11800 | Streebog-512 | Streebog | +6.5% | 187.2 → 199.3 | WIN +6.5% ✅ | `autoresearch/11800-jul6` |
| C | 11700 | Streebog-256 | Streebog | +5.7% | 188.8 → 199.5 | WIN +5.7% ✅ | `autoresearch/11700-jul6` |
| C | 31100 | SM3 | SM3 | +3.2% | 7.2k → 7.5k | WIN +3.2% ✅ | `autoresearch/31100-jul6` |
| C | 6100 | Whirlpool (campaign ext.) | Whirlpool | +2.0% | 1.5k → 1.6k | WIN +2.0% ❌ rejected | `autoresearch/6100-jul6` |
| C | 6900 | GOST R 34.11-94 | GOST | ~0% | 934.8 → 934.8 | roofline | `autoresearch/6900-jul6` |
| C | 600 | BLAKE2b-512 | BLAKE2 | ~0% | 5.2k → 5.2k | roofline | `autoresearch/600-jul6` |
| C | 1700 | SHA2-512 | SHA2 | ~0% | 2.9k → 2.9k | roofline | `autoresearch/1700-jul6` |
| C | 10800 | SHA2-384 | SHA2 | ~0% | 2.9k → 2.9k | roofline | `autoresearch/10800-jul6` |
| C | 6000 | RIPEMD-160 | RIPEMD | ~0% | 14.2k → 14.2k | roofline | `autoresearch/6000-jul6` |
| 1 | 18000 | Keccak-512 | SHA3/Keccak | +9.9% | 1.9k → 2.1k | WIN +9.9% (partial 1/6) | `autoresearch/18000-jul6` |
| 1 | 17700 | Keccak-224 | SHA3/Keccak | +9.8% | 1.9k → 2.1k | WIN +9.8% (partial 1/6) | `autoresearch/17700-jul6` |
| 1 | 17300 | SHA3-224 | SHA3/Keccak | +5.1% | 1.9k → 2.0k | WIN +5.1% (partial 1/6) | `autoresearch/17300-jul6` |
| 1 | 17500 | SHA3-384 | SHA3/Keccak | — | 1.9k → 1.9k | NOT-RUN (spend-limit) | `autoresearch/17500-jul6` |
| 1 | 17900 | Keccak-384 | SHA3/Keccak | — | 1.9k → 1.9k | NOT-RUN (spend-limit) | `autoresearch/17900-jul6` |
| 2 | 27000 | NetNTLMv1-NT (slow) | AD-auth | +19.6% | 931.5 → 1.1k | WIN +19.6% | `autoresearch/27000-jul6` |
| 2 | 1000 | NTLM | AD-auth | +3.1% | 119.2k → 122.9k | WIN +3.1% | `autoresearch/1000-jul6` |
| 2 | 3000 | LM | AD-auth | — | 60.9k → 60.9k | NOT-RUN (spend-limit) | `autoresearch/3000-jul6` |
| 2 | 5500 | NetNTLMv1 | AD-auth | ~0% | 46.2k → 46.2k | roofline | `autoresearch/5500-jul6` |
| 2 | 5600 | NetNTLMv2 | AD-auth | ~0% | 4.7k → 4.7k | roofline | `autoresearch/5600-jul6` |
| 3 | 9700 | MS Office <=2003 MD5+RC4 | Office | +22.4% | 1.0k → 1.3k | WIN +22.4% (partial 5/6) | `autoresearch/9700-jul6` |
| 3 | 19600 | Kerberos etype17 TGS-REP AES128 (slow) | Kerberoasting | ~0% | 2.2 → 2.2 | in-progress 5/6 | `autoresearch/19600-jul6` |
| 3 | 19700 | Kerberos etype18 TGS-REP AES256 (slow) | Kerberoasting | ~0% | 1.1 → 1.1 | in-progress 5/6 | `autoresearch/19700-jul6` |
| 3 | 18200 | Kerberos etype23 AS-REP RC4 | AS-REP-roast | ~0% | 1.4k → 1.4k | in-progress 3/6 | `autoresearch/18200-jul6` |
| 3 | 9800 | MS Office <=2003 SHA1+RC4 | Office | ~0% | 1.2k → 1.2k | in-progress 4/6 | `autoresearch/9800-jul6` |
| 4 | 9400 | MS Office 2007 (slow) | Office | — | 0.4 → 0.4 | NOT-RUN (spend-limit) | `autoresearch/9400-jul6` |
| 4 | 9500 | MS Office 2010 (slow) | Office | — | 0.2 → 0.2 | NOT-RUN (spend-limit) | `autoresearch/9500-jul6` |
| 4 | 9600 | MS Office 2013 (slow) | Office |  |  | pending | `autoresearch/9600-jul6` |
| 4 | 1100 | DCC / MS Cache | MSCache | — | 32.2k → 32.2k | NOT-RUN (spend-limit) | `autoresearch/1100-jul6` |
| 4 | 2100 | DCC2 / MS Cache 2 (slow) | MSCache | — | 0.9 → 0.9 | NOT-RUN (spend-limit) | `autoresearch/2100-jul6` |
| 5 | 0 | MD5 | Raw |  |  | - | `-` |
| 5 | 100 | SHA1 | Raw |  |  | - | `-` |
| 5 | 1400 | SHA2-256 | Raw |  |  | - | `-` |
| 5 | 900 | MD4 | Raw |  |  | - | `-` |
| 5 | 1300 | SHA2-224 | Raw |  |  | - | `-` |
| 6 | 10 | md5(pass.salt) | Salted |  |  | - | `-` |
| 6 | 110 | sha1(pass.salt) | Salted |  |  | - | `-` |
| 6 | 1410 | sha256(pass.salt) | Salted |  |  | - | `-` |
| 6 | 5100 | Half-MD5 | Salted |  |  | - | `-` |
| 6 | 2600 | md5(md5(pass)) | Salted |  |  | - | `-` |
| 7 | 3200 | bcrypt | Unix-KDF |  |  | - | `-` |
| 7 | 500 | md5crypt | Unix-KDF |  |  | - | `-` |
| 7 | 1800 | sha512crypt | Unix-KDF |  |  | - | `-` |
| 7 | 7400 | sha256crypt | Unix-KDF |  |  | - | `-` |
| 7 | 400 | phpass | Unix-KDF |  |  | - | `-` |
| 8 | 12000 | PBKDF2-HMAC-SHA1 | PBKDF2/WPA/DB |  |  | - | `-` |
| 8 | 10900 | PBKDF2-HMAC-SHA256 | PBKDF2/WPA/DB |  |  | - | `-` |
| 8 | 22000 | WPA-PBKDF2-PMKID+EAPOL | PBKDF2/WPA/DB |  |  | - | `-` |
| 8 | 300 | MySQL4.1/5 | PBKDF2/WPA/DB |  |  | - | `-` |
| 8 | 1731 | MSSQL 2012/2014 | PBKDF2/WPA/DB |  |  | - | `-` |
| 9 | 10500 | PDF 1.4-1.6 | Docs/Wallet |  |  | - | `-` |
| 9 | 11300 | Bitcoin/Litecoin wallet.dat | Docs/Wallet |  |  | - | `-` |
| 9 | 7900 | Drupal7 | Docs/Wallet |  |  | - | `-` |
| 9 | 112 | Oracle 11+ | Docs/Wallet |  |  | - | `-` |
| 9 | 15700 | Ethereum Wallet SCRYPT | Docs/Wallet |  |  | - | `-` |
| 10 | 14600 | LUKS v1 | AES-container |  |  | - | `-` |
| 10 | 13751 | VeraCrypt SHA256+AES XTS512 | AES-container |  |  | - | `-` |
| 10 | 6211 | TrueCrypt RIPEMD160+AES XTS512 | AES-container |  |  | - | `-` |
| 10 | 6221 | TrueCrypt SHA512+AES XTS512 | AES-container |  |  | - | `-` |
| 10 | 16700 | FileVault 2 | AES-container |  |  | - | `-` |
| 11 | 13752 | VeraCrypt SHA256 XTS1024 | Twofish/Serpent |  |  | - | `-` |
| 11 | 13753 | VeraCrypt SHA256 XTS1536 | Twofish/Serpent |  |  | - | `-` |
| 11 | 6212 | TrueCrypt RIPEMD160 XTS1024 | Twofish/Serpent |  |  | - | `-` |
| 11 | 6213 | TrueCrypt RIPEMD160 XTS1536 | Twofish/Serpent |  |  | - | `-` |
| 11 | 13763 | VeraCrypt SHA256 boot | Twofish/Serpent |  |  | - | `-` |
| 12 | 13771 | VeraCrypt Streebog512 XTS512 | Kuznyechik/Streebog |  |  | pending | `-` |
| 12 | 13772 | VeraCrypt Streebog512 XTS1024 | Kuznyechik/Streebog |  |  | pending | `-` |
| 12 | 11750 | HMAC-Streebog-256 (key=pass) | Kuznyechik/Streebog |  |  | pending | `-` |
| 12 | 11760 | HMAC-Streebog-256 (key=salt) | Kuznyechik/Streebog |  |  | pending | `-` |
| 12 | 6800 | LastPass | Kuznyechik/Streebog |  |  | pending | `-` |
| 13 | 12100 | PBKDF2-HMAC-SHA512 | SHA512/256-KDF |  |  | - | `-` |
| 13 | 7100 | macOS v10.8+ PBKDF2-SHA512 | SHA512/256-KDF |  |  | - | `-` |
| 13 | 6600 | 1Password agilekeychain | SHA512/256-KDF |  |  | - | `-` |
| 13 | 9200 | Cisco-IOS $8$ PBKDF2-SHA256 | SHA512/256-KDF |  |  | - | `-` |
| 13 | 15300 | DPAPI masterkey v1 | SHA512/256-KDF |  |  | - | `-` |
| 14 | 8900 | scrypt | scrypt/misc |  |  | - | `-` |
| 14 | 22700 | MultiBit HD scrypt | scrypt/misc |  |  | - | `-` |
| 14 | 15900 | DPAPI masterkey v2 | scrypt/misc |  |  | - | `-` |
| 14 | 25400 | PDF 1.4-1.6 user+owner | scrypt/misc |  |  | - | `-` |
| 14 | 21600 | Web2py pbkdf2-sha512 | scrypt/misc |  |  | - | `-` |

**Totals:** 13 wins across 76 evaluated modes. Verified-real: 6. Rejected: 1.
