# Cedar Backup v3

![](https://img.shields.io/pypi/l/CedarBackup3.svg)
![](https://img.shields.io/pypi/wheel/CedarBackup3.svg)
![](https://img.shields.io/pypi/pyversions/CedarBackup3.svg)
![](https://github.com/pronovic/cedar-backup3/workflows/Test%20Suite/badge.svg)
![](https://readthedocs.org/projects/CedarBackup3/badge/?version=latest&style=flat)

Cedar Backup is a software package designed to manage system backups for a
pool of local and remote machines.  Cedar Backup understands how to back up
filesystem data as well as MySQL and PostgreSQL databases and Subversion
repositories.  It can also be easily extended to support other kinds of
data sources.

Cedar Backup is focused around weekly backups to a single CD or DVD disc,
with the expectation that the disc will be changed or overwritten at the
beginning of each week.  If your hardware is new enough, Cedar Backup can
write multisession discs, allowing you to add incremental data to a disc on
a daily basis.  

Alternately, Cedar Backup can write your backups to the Amazon S3 cloud
rather than relying on physical media.

Besides offering command-line utilities to manage the backup process, Cedar
Backup provides a well-organized library of backup-related functionality,
written in the Python 3 programming language.

This is release 3 of the Cedar Backup package.  Release 3 is a Python 3
conversion of release 2, with minimal additional functionality. 

CedarBackup2 and CedarBackup3 are functionally equivalent and are
compatible with one another.  It is safe to mix-and-match clients running
both versions within the same backup configuration.

