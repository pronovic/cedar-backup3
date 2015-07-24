#!/usr/bin/python
# Sort the output of 'svn list --verbose' on a tags directory, by version
# The output is assumed to be piped in.

# pylint: disable=C0111,C0103

import sys
import re

def compare(x, y):
   """Compare two 'svn list --verbose' lines by numified version."""
   return cmp(numify(x), numify(y))

def numify(x):
   """Numify a 'svn list --verbose' line, extracting the version and making it into a float."""
   if re.match("^.*CEDAR_BACKUP2_V", x):
      x = re.sub("^.*CEDAR_BACKUP2_V", "", x)
      x = re.sub("/", "", x)
      x = re.sub("\n", "", x)
      components = x.split(".")
      numified = components[0]
      numified += "."
      for component in components[1:]:
         component = re.sub("[^0-9].*$", "", component)
         numified += "%03d" % int(component)
      return float(numified)
   return 0 # ignore the line if we can't parse it

lines = sys.stdin.readlines()
lines.sort(compare)
for line in lines:
   sys.stdout.write(line)
