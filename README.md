# Cedar Backup v3

[![pypi](https://img.shields.io/pypi/v/cedar-backup3.svg)](https://pypi.org/project/cedar-backup3/)
[![license](https://img.shields.io/pypi/l/cedar-backup3.svg)](https://github.com/pronovic/cedar-backup3/blob/master/LICENSE)
[![wheel](https://img.shields.io/pypi/wheel/cedar-backup3.svg)](https://pypi.org/project/cedar-backup3/)
[![python](https://img.shields.io/pypi/pyversions/cedar-backup3.svg)](https://pypi.org/project/cedar-backup3/)
[![Test Suite](https://github.com/pronovic/cedar-backup3/workflows/Test%20Suite/badge.svg)](https://github.com/pronovic/cedar-backup3/actions?query=workflow%3A%22Test+Suite%22)
[![docs](https://readthedocs.org/projects/cedar-backup3/badge/?version=stable&style=flat)](https://cedar-backup3.readthedocs.io/en/stable/)

## What is Cedar Backup?

[Cedar Backup v3](https://pypi.org/project/cedar-backup3/) is a software
package designed to manage system backups for a pool of local and remote
machines. The project was originally maintained at SourceForge, and historical
releases still exist there. The project was moved to BitBucket in mid-2015, and
from there to GitHub in mid-2019 when BitBucket retired their Mercurial hosting
service.

Cedar Backup understands how to back up filesystem data as well as MySQL and
PostgreSQL databases and Subversion repositories. It can also be easily extended 
to support other kinds of data sources.  The backup process is focused around 
weekly backups to a single CD or DVD disc, with the expectation that the disc 
will be changed or overwritten at the beginning of each week. Alternately, 
Cedar Backup can write your backups to the Amazon S3 cloud rather than relying 
on physical media.

Besides offering command-line utilities to manage the backup process, Cedar
Backup provides a well-organized library of backup-related functionality,
written in the Python 3 programming language.

There are many different backup software systems in the open source world.
Cedar Backup aims to fill a niche: it aims to be a good fit for people who need
to back up a limited amount of important data on a regular basis. Cedar Backup
isn’t for you if you want to back up your huge MP3 collection every night, or
if you want to back up a few hundred machines.  However, if you administer a
small set of machines and you want to run daily incremental backups for things
like system configuration, current email, small web sites, source code
repositories, or small databases, then Cedar Backup is probably worth your
time.

Cedar Backup has been developed on a [Debian GNU/Linux](http://www.debian.org/) system 
and is primarily supported on Debian and other Linux systems.  However, since it is written 
in portable [Python 3](http://www.python.org), it should run without problems on
just about any UNIX-like operating system. In particular, full Cedar
Backup functionality is known to work on Debian and SuSE Linux, and client 
functionality is also known to work on FreeBSD and OS X systems.

## Developer Documentation

Developer documentation is found in [DEVELOPER.md](DEVELOPER.md).  See that
file for notes about how the code is structured, how to set up a development
environment, etc.

## End User Documentation

See the [Changelog](https://github.com/pronovic/cedar-backup3/blob/master/Changelog) for
recent changes.

The [Cedar Backup v3 Software Manual](https://cedar-backup3.readthedocs.io/en/stable/manual/index.html) documents 
the process of setting up and using Cedar Backup.  In the manual, you can find
information about how Cedar Backup works, how to install and configure it, how
to schedule backups, how to restore data, and how to get support.

## Library Code

The Cedar Backup v3 has been designed as both an application and a
library of backup-related functionality.  The `CedarBackup3` Python 
package contains a variety of useful backup-related classes and functions.  For
instance: the `IsoImage` class represents an ISO CD image;
the `CdWriter` class represents a CD-R/CD-RW writer device; and the
`FilesystemList` class represents a list of files and directories on a
filesystem.  For more information, see 
the [API Reference](https://cedar-backup3.readthedocs.io/en/stable/autoapi/index.html) documentation.

## Package Distributions

Cedar Backup is primarily distributed as a Python 3 package.  You can install
it from [PyPI](https://pypi.org/project/cedar-backup3/) using pip:

```
$ pip install cedar-backup3
```

In addition to the Python package, Cedar Backup requires a variety of external 
system dependencies.  For more information, see 
the [Cedar Backup v3 Software Manual](https://cedar-backup3.readthedocs.io/en/stable/manual/install.html#installing-the-python-package).
    
Debian packages for Cedar Backup v3, called `cedar-backup3` and
`cedar-backup3-doc`, were first available starting with the Debian 'stretch'
release.  Debian derivatives (such as Ubuntu) should also contain the packages.
