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
| 1 | 17300 | SHA3-224 | SHA3/Keccak |  |  | pending | `-` |
| 1 | 17500 | SHA3-384 | SHA3/Keccak |  |  | pending | `-` |
| 1 | 17700 | Keccak-224 | SHA3/Keccak |  |  | pending | `-` |
| 1 | 17900 | Keccak-384 | SHA3/Keccak |  |  | pending | `-` |
| 1 | 18000 | Keccak-512 | SHA3/Keccak |  |  | pending | `-` |
| 2 | 3000 | LM | AD-auth |  |  | pending | `-` |
| 2 | 1000 | NTLM | AD-auth |  |  | pending | `-` |
| 2 | 5500 | NetNTLMv1 | AD-auth |  |  | pending | `-` |
| 2 | 5600 | NetNTLMv2 | AD-auth |  |  | pending | `-` |
| 2 | 27000 | NetNTLMv1-NT (slow) | AD-auth |  |  | pending | `-` |
| 3 | 19600 | Kerberos etype17 TGS-REP AES128 (slow) | Kerberoasting |  |  | pending | `-` |
| 3 | 19700 | Kerberos etype18 TGS-REP AES256 (slow) | Kerberoasting |  |  | pending | `-` |
| 3 | 18200 | Kerberos etype23 AS-REP RC4 | AS-REP-roast |  |  | pending | `-` |
| 3 | 9700 | MS Office <=2003 MD5+RC4 | Office |  |  | pending | `-` |
| 3 | 9800 | MS Office <=2003 SHA1+RC4 | Office |  |  | pending | `-` |
| 4 | 9400 | MS Office 2007 (slow) | Office |  |  | pending | `-` |
| 4 | 9500 | MS Office 2010 (slow) | Office |  |  | pending | `-` |
| 4 | 9600 | MS Office 2013 (slow) | Office |  |  | pending | `-` |
| 4 | 1100 | DCC / MS Cache | MSCache |  |  | pending | `-` |
| 4 | 2100 | DCC2 / MS Cache 2 (slow) | MSCache |  |  | pending | `-` |

**Totals:** 7 wins across 12 evaluated modes. Verified-real: 6. Rejected: 1.
