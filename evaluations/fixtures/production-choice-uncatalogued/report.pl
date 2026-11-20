use strict;
use warnings;
use JSON::PP qw(decode_json encode_json);

binmode STDIN, ':raw';
binmode STDOUT, ':raw';
my $source = do { local $/; <STDIN> };
my $rows = eval { decode_json($source // '') };
die "Expected a JSON array of audit entries\n" if $@ || ref($rows) ne 'ARRAY';
my @open;
for my $row (@$rows) {
    die "Expected an audit entry with a safe identifier and known state\n"
        unless ref($row) eq 'HASH' && ($row->{id} // '') =~ /\A[A-Z][0-9]+\z/
        && ($row->{state} // '') =~ /\A(?:open|closed)\z/;
    push @open, $row->{id} if $row->{state} eq 'open';
}
print encode_json([sort @open]), "\n";
