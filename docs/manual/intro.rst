.. _cedar-intro:

Introduction
============

   “Only wimps use tape backup: real men just upload their important
   stuff on ftp, and let the rest of the world mirror it.”--- Linus
   Torvalds, at the release of Linux 2.0.8 in July of 1996.

.. _cedar-intro-whatis:

What is Cedar Backup?
---------------------

Cedar Backup is a software package designed to manage system backups for
a pool of local and remote machines. Cedar Backup understands how to
back up filesystem data as well as MySQL and PostgreSQL databases and
Subversion repositories. It can also be easily extended to support other
kinds of data sources.

Cedar Backup is focused around weekly backups to a single CD or DVD
disc, with the expectation that the disc will be changed or overwritten
at the beginning of each week. If your hardware is new enough (and
almost all hardware is today), Cedar Backup can write multisession
discs, allowing you to add incremental data to a disc on a daily basis.

Alternately, Cedar Backup can write your backups to the Amazon S3 cloud
rather than relying on physical media.

Besides offering command-line utilities to manage the backup process,
Cedar Backup provides a well-organized library of backup-related
functionality, written in the Python 3 programming language.

There are many different backup software systems in the open source world.
Cedar Backup aims to fill a niche: it aims to be a good fit for people who need
to back up a limited amount of important data on a regular basis. Cedar Backup
isn’t for you if you want to back up your huge MP3 collection every night, or
if you want to back up a few hundred machines.  However, if you administer a
small set of machines and you want to run daily incremental backups for things
like system configuration, current email, small web sites, source code
repositories, or small databases, then Cedar Backup is probably worth your
time.

Cedar Backup has been developed on a Debian GNU/Linux system and is
primarily supported on Debian and other Linux systems. However, since it
is written in portable Python 3, it should run without problems on just
about any UNIX-like operating system. In particular, full Cedar Backup
functionality is known to work on Debian and SuSE Linux systems, and
client functionality is also known to work on FreeBSD and Mac OS X
systems.

To run a Cedar Backup client, you really just need a working Python 3
installation. To run a Cedar Backup master, you will also need a set of
other executables, most of which are related to building and writing
CD/DVD images or talking to the Amazon S3 infrastructure. A full list of
dependencies is provided in :doc:`install`.

.. _cedar-intro-migrating:

Migrating from Version 2 to Version 3
-------------------------------------

The main difference between Cedar Backup version 2 and Cedar Backup
version 3 is the targeted Python interpreter. Cedar Backup version 2 was
designed for Python 2, while version 3 is a conversion of the original
code to Python 3. Other than that, both versions are functionally
equivalent. The configuration format is unchanged, and you can
mix-and-match masters and clients of different versions in the same
backup pool. Python 2 has now reached its end of life, and Cedar Backup v2 has
been unsupported since 11 Nov 2017.

A major design goal for version 3 was to facilitate easy migration testing for
users, by making it possible to install version 3 on the same server where
version 2 was already in use. A side effect of this design choice is that all
of the executables, configuration files, and logs changed names in version 3.
Where version 2 used ``cback``, version 3 uses ``cback3``: ``cback3.conf``
instead of ``cback.conf``, ``cback3.log`` instead of ``cback.log``, etc.

So, while migrating from version 2 to version 3 is relatively
straightforward, you will have to make some changes manually. You will
need to create a new configuration file (or soft link to the old one),
modify your cron jobs to use the new executable name, etc. You can
migrate one server at a time in your pool with no ill effects, or even
incrementally migrate a single server by using version 2 and version 3
on different days of the week or for different parts of the backup.

.. _cedar-intro-support:

How to Get Support
------------------

Cedar Backup is open source software that is provided to you at no cost.
It is provided with no warranty, not even for MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. However, that said, someone can usually help
you solve whatever problems you might see.

If you experience a problem, your best bet is to file an issue in the
issue tracker at GitHub.  [1]_ When the source code was hosted at
SourceForge, there was a mailing list. However, it was very lightly used
in the last years before I abandoned SourceForge, and I have decided not
to replace it.

If you are not comfortable discussing your problem in public or listing
it in a public database, or if you need to send along information that
you do not want made public, then you can write
support@cedar-solutions.com. That mail will go directly to me. If you
write the support address about a bug, a “scrubbed” bug report will
eventually end up in the public bug database anyway, so if at all
possible you should use the public reporting mechanisms. One of the
strengths of the open-source software development model is its
transparency.

Regardless of how you report your problem, please try to provide as much
information as possible about the behavior you observed and the
environment in which the problem behavior occurred.  [2]_

In particular, you should provide: the version of Cedar Backup that you
are using; how you installed Cedar Backup (i.e. Debian package, source
package, etc.); the exact command line that you executed; any error
messages you received, including Python stack traces (if any); and
relevant sections of the Cedar Backup log. It would be even better if
you could describe exactly how to reproduce the problem, for instance by
including your entire configuration file and/or specific information
about your system that might relate to the problem. However, please do
*not* provide huge sections of debugging logs unless you are sure they
are relevant or unless someone asks for them.

   |tip|

   Sometimes, the error that Cedar Backup displays can be rather
   cryptic. This is because under internal error conditions, the text
   related to an exception might get propogated all of the way up to the
   user interface. If the message you receive doesn't make much sense,
   or if you suspect that it results from an internal error, you might
   want to re-run Cedar Backup with the ``--stack`` option. This forces
   Cedar Backup to dump the entire Python stack trace associated with
   the error, rather than just printing the last message it received.
   This is good information to include along with a bug report, as well.

.. _cedar-intro-history:

History
-------

Cedar Backup began life in late 2000 as a set of Perl scripts called
kbackup. These scripts met an immediate need (which was to back up
skyjammer.com and some personal machines) but proved to be unstable,
overly verbose and rather difficult to maintain.

In early 2002, work began on a rewrite of kbackup. The goal was to
address many of the shortcomings of the original application, as well as
to clean up the code and make it available to the general public. While
doing research related to code I could borrow or base the rewrite on, I
discovered that there was already an existing backup package with the
name kbackup, so I decided to change the name to Cedar Backup instead.

Because I had become fed up with the prospect of maintaining a large volume of
Perl code, I decided to abandon that language in favor of Python.  At the time,
I chose Python mostly because I was interested in learning it, but in
retrospect it turned out to be a very good decision.

Around this same time, skyjammer.com and cedar-solutions.com were
converted to run Debian GNU/Linux and I entered the Debian new maintainer
queue, so I also made it a goal to implement Debian packages along with a
Python source distribution for the new release.

Version 1.0 of Cedar Backup was released in June of 2002. We immediately
began using it to back up skyjammer.com and cedar-solutions.com, where
it proved to be much more stable than the original code.

In the meantime, I continued to improve as a Python programmer and also
started doing a significant amount of professional development in Java.
It soon became obvious that the internal structure of Cedar Backup 1.0,
while much better than kbackup, still left something to be desired. In
November 2003, I began an attempt at cleaning up the codebase. I
converted all of the internal documentation to use Epydoc,  and
updated the code to use the newly-released Python logging package
after having a good experience with Java's log4j. However, I was still
not satisfied with the code, which did not lend itself to the automated
regression testing I had used when working with JUnit in my Java code.

So, rather than releasing the cleaned-up code, I instead began another
ground-up rewrite in May 2004. With this rewrite, I applied everything I
had learned from other Java and Python projects I had undertaken over
the last few years. I structured the code to take advantage of Python's
unique ability to blend procedural code with object-oriented code, and I
made automated unit testing a primary requirement. The result was the
2.0 release, which was cleaner, more compact, better focused, and better
documented than any release before it. Utility code is less
application-specific, and is now usable as a general-purpose library.
The 2.0 release also includes a complete regression test suite of over
3800 tests, which will help to ensure that quality is maintained as
development continues into the future. 

The 3.0 release of Cedar Backup is a Python 3 conversion of the 2.0 release,
with minimal additional functionality. The conversion from Python 2 to Python 3
started in mid-2015, about 5 years before the anticipated deprecation of Python
2 in 2020.  In 2020, the Python package structure, development tooling, and
documentation format were modernized, preparing Cedar Backup for the next phase
of its life.
         
----------

*Previous*: :doc:`preface` • *Next*: :doc:`basic`

----------

.. [1]
   See `<https://github.com/pronovic/cedar-backup3/issues>`__

.. [2]
   See Simon Tatham's excellent bug reporting tutorial:
   `<http://www.chiark.greenend.org.uk/~sgtatham/bugs.html>`__ .

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png

