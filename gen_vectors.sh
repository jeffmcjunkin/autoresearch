#!/bin/bash
# Run under WSL perl: generate independent-reference word/hash pairs for the confirmed wins.
cd /mnt/c/Users/jeff/Documents/hashcat || exit 1
mkdir -p /mnt/c/Users/jeff/Documents/autoresearch/pv
for M in 9700 17700 18000 3000 17500 17300 17900 10500 18200; do
  perl tools/test.pl single "$M" 2>/dev/null > /mnt/c/Users/jeff/Documents/autoresearch/pv/gen_$M.txt
done
wc -l /mnt/c/Users/jeff/Documents/autoresearch/pv/gen_*.txt
