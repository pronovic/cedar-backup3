[![pypi](https://img.shields.io/pypi/v/cedar-backup3.svg)](https://pypi.org/project/cedar-backup3/)
[![license](https://img.shields.io/pypi/l/cedar-backup3.svg)](https://github.com/pronovic/cedar-backup3/blob/master/LICENSE)
[![wheel](https://img.shields.io/pypi/wheel/cedar-backup3.svg)](https://pypi.org/project/cedar-backup3/)
[![python](https://img.shields.io/pypi/pyversions/cedar-backup3.svg)](https://pypi.org/project/cedar-backup3/)
[![Test Suite](https://github.com/pronovic/cedar-backup3/workflows/Test%20Suite/badge.svg)](https://github.com/pronovic/cedar-backup3/actions?query=workflow%3A%22Test+Suite%22)
[![docs](https://readthedocs.org/projects/cedar-backup3/badge/?version=stable&style=flat)](https://cedar-backup3.readthedocs.io/en/stable/)

[Cedar Backup](https://github.com/pronovic/cedar-backup3) is a software package
designed to manage system backups for a pool of local and remote machines.
Cedar Backup understands how to back up filesystem data as well as MySQL and
PostgreSQL databases and Subversion repositories.  It can also be easily
extended to support other kinds of data sources.

Cedar Backup is focused around weekly backups to a single CD or DVD disc,
with the expectation that the disc will be changed or overwritten at the
beginning of each week.  If your hardware is new enough, Cedar Backup can
write multisession discs, allowing you to add incremental data to a disc on
a daily basis.  Alternately, Cedar Backup can write your backups to the Amazon
S3 cloud rather than relying on physical media.  See 
the [Cedar Backup v3 Software Manual](https://cedar-backup3.readthedocs.io/en/stable/manual/index.html) for details.

Besides offering command-line utilities to manage the backup process, Cedar
Backup provides a well-organized library of backup-related functionality.
For more information, see 
the [API Reference](https://cedar-backup3.readthedocs.io/en/stable/autoapi/index.html).

There are many different backup software systems in the open source world.
Cedar Backup aims to fill a niche: it aims to be a good fit for people who need
to back up a limited amount of important data on a regular basis. Cedar Backup
isn’t for you if you want to back up your huge MP3 collection every night, or
if you want to back up a few hundred machines.  However, if you administer a
small set of machines and you want to run daily incremental backups for things
like system configuration, current email, small web sites, source code
repositories, or small databases, then Cedar Backup is probably worth your
time.
