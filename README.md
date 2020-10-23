# Cedar Backup v3

## What is Cedar Backup?

Cedar Backup is a software package designed to manage system backups for a pool
of local and remote machines. The project was originally maintained at 
[SourceForge](http://sourceforge.net/projects/cedar-backup/), 
and historical releases still exist there. The project was moved to BitBucket in
mid-2015, and from there to GitHub in mid-2019 when BitBucket retired their
Mercurial hosting service.

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

There are many different backup software implementations out there in the open 
source world. Cedar Backup aims to fill a niche: it aims to
be a good fit for people who need to back up a limited amount of important data
on a regular basis. Cedar Backup isn't for you if you want to back
up your huge MP3 collection every night, or if you want to back up a few hundred
machines. However, if you administer a small set of machines and you want to
run daily incremental backups for things like system configuration, current
email, small web sites, source code repositories, or small databases, then 
Cedar Backup is probably worth your time.

Cedar Backup has been developed on a 
[Debian GNU/Linux](http://www.debian.org/)
system and is primarily supported on Debian and other Linux systems.
However, since it is written in portable 
[Python 3](http://www.python.org), it should run without problems on
just about any UNIX-like operating system. In particular, full Cedar
Backup functionality is known to work on Debian and SuSE Linux, and client 
functionality is also known to work on FreeBSD and OS X systems.

## Developer Documentation

Developer documentation is found in [DEVELOPER.md](DEVELOPER.md).  See that
file for notes about how the code is structured, how to set up a development
environment, etc.

## End User Documentation

See the [Changelog](https://github.com/cedarsolutions/cedar-backup3/blob/master/Changelog) for
recent changes.

The Cedar Backup Software Manual documents the process of setting up and using
Cedar Backup.  In the manual, you can find information about how Cedar Backup
works, how to install and configure it, how to schedule backups, how to restore
data, and how to get support.

The following versions of the manual are available:

* [Single-page HTML](https://cedarsolutions.github.io/cedar-backup3/docs/manual/manual.html)
* [Multiple-page HTML](https://cedarsolutions.github.io/cedar-backup3/docs/manual/index.html)

Most users will want to look at the multiple-page HTML version.

## Library Code

The Cedar Backup version 3 has been designed as both an application and a
library of backup-related functionality.  The `CedarBackup3` Python 
package contains a variety of useful backup-related classes and functions.  For
instance: the `IsoImage` class represents an ISO CD image;
the `CdWriter` class represents a CD-R/CD-RW writer device; and the
`FilesystemList` class represents a list of files and directories on a
filesystem.  For more information, see the 
[public interface documentation](https://cedarsolutions.github.io/cedar-backup3/docs/interface), 
generated from the source code using [Sphinx Napolean](http://www.sphinx-doc.org/en/stable/ext/napoleon.html).

## Package Distributions

Cedar Backup is primarily distributed as a Python 3 source package.  You can
download the latest release from GitHub.

Debian packages for Cedar Backup v3, called `cedar-backup3` and
`cedar-backup3-doc`, were first available starting with the Debian 'stretch'
release.  Debian derivatives (such as Ubuntu) should also contain the packages.

Debian users who who want to always run the latest release of Cedar Backup rather than the version 
included with their distribution can use the Cedar Solutions APT source.  See the Cedar Solutions 
[Debian page](http://software.cedar-solutions.com/debian.html) for more information.

## Support

If you think you have found a bug or you would like to request an enhancement,
file an issue on the GitHub issue tracker.

## Contributing Improvements

Users are welcome to contribute improvements to Cedar Backup.  In the past,
users have helped out by reporting unit test failures, making suggestions,
requesting enhancements, updating documentation, submitting patches, and
beta-testing entire releases or individual bug fixes.  As a result, Cedar
Backup has evolved into a much more flexible platform than it would otherwise
have been.  If you are interested in contributing, submit a PR at GitHub.

## Migrating from Version 2 to Version 3

The main difference between Cedar Backup version 2 and Cedar Backup version 3
is the targeted Python interpreter.  Cedar Backup version 2 was designed for
Python 2, while version 3 is a conversion of the original code to Python 3.
Other than that, both versions are functionally equivalent.  The configuration
format is unchanged, and you can mix-and-match masters and clients of different
versions in the same backup pool.  However, version 2 is no longer maintained, 
so you should convert as soon as possible.

A major design goal for version 3 was to facilitate easy migration testing for
users, by making it possible to install version 3 on the same server where
version 2 was already in use.  A side effect of this design choice is that all
of the executables, configuration files, and logs changed names in version 3.
Where version 2 used `cback`, version 3 uses `cback3`: `cback3.conf` instead of
`cback.conf`, `cback3.log` instead of `cback.log`, etc.

So, while migrating from version 2 to version 3 is relatively straightforward,
you will have to make some changes manually.  You will need to create a new
configuration file (or soft link to the old one), modify your cron jobs to use
the new executable name, etc.  You can migrate one server at a time in your
pool with no ill effects, or even incrementally migrate a single server by
using version 2 and version 3 on different days of the week or for different
parts of the backup.
