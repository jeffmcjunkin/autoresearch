#!/bin/bash
cd /mnt/c/Users/jeff/Documents/hashcat || exit 1
for M in 11700 11800 17400 17600; do
  perl tools/test.pl single "$M" 2>/mnt/c/Users/jeff/Documents/autoresearch/pv/err_$M.txt > /mnt/c/Users/jeff/Documents/autoresearch/pv/gen_$M.txt
  printf "m%s: %s hashes  %s\n" "$M" "$(grep -c . /mnt/c/Users/jeff/Documents/autoresearch/pv/gen_$M.txt)" "$(head -1 /mnt/c/Users/jeff/Documents/autoresearch/pv/err_$M.txt)"
done
