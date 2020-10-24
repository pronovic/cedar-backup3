# Generates 100,000 lines of output (about 4 MB of data).
# The first argument says where to put the lines.
# "stdout" goes to stdout
# "stderr" goes to stdrer
# "both" duplicates the line to both stdout and stderr

import sys

where = "both"
if len(sys.argv) > 1:
    where = sys.argv[1]

for i in range(1, 100000 + 1):
    if where == "both":
        sys.stdout.write("This is line %d.\n" % i)
        sys.stderr.write("This is line %d.\n" % i)
    elif where == "stdout":
        sys.stdout.write("This is line %d.\n" % i)
    elif where == "stderr":
        sys.stderr.write("This is line %d.\n" % i)
