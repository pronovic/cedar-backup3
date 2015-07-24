Through Cedar Backup 2.19.2, I supported the user manual in the PDF format.
Unfortunately, the toolchain changed in early 2009 (when Debian lenny was
released) and I can no longer build the PDF format properly.  The existing
FOP-based solution simply blows up, and the other alternatives I looked at
(such as 'xmlto pdf') don't work, either.

As a result, I am removing support for the PDF documentation.  I don't
think it is heavily utilized, and I can't find the time or motivation right
now to fight with the toolchain.  To be honest, I'm quite frustrated that
somthing which has worked fine for so long is completely broken now.  Maybe
I'm just missing something completely obvious, but I can't find it.

This directory contains the various files that I orphaned when removing PDF
support.  If/when I get PDFs working properly again, this stuff will either
be integrated back into the codebase proper, or will get removed completely
(since it will be obsolete).

KJP
29 Mar 2009
