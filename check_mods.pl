for my $m (qw/Crypt::RC4 Digest::MD5 Digest::SHA Digest::SHA3 Digest::Keccak Digest::MD4 Digest::HMAC_MD5 Crypt::PBKDF2 Authen::Passphrase::LANManager MIME::Base64 Encode/) {
    my $ok = eval "require $m; 1";
    printf "%-38s %s\n", $m, ($ok ? "ok" : "MISSING");
}
