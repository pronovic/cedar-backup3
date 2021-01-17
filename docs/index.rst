Cedar Backup v3
===============

Release v\ |version|

.. image:: https://img.shields.io/pypi/v/cedar-backup3.svg
    :target: https://pypi.org/project/cedar-backup3/

.. image:: https://img.shields.io/pypi/l/cedar-backup3.svg
    :target: https://github.com/pronovic/cedar-backup3/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/wheel/cedar-backup3.svg
    :target: https://pypi.org/project/cedar-backup3/

.. image:: https://img.shields.io/pypi/pyversions/cedar-backup3.svg
    :target: https://pypi.org/project/cedar-backup3/

.. image:: https://github.com/pronovic/cedar-backup3/workflows/Test%20Suite/badge.svg
    :target: https://github.com/pronovic/cedar-backup3/actions?query=workflow%3A%22Test+Suite%22

.. image:: https://readthedocs.org/projects/cedar-backup3/badge/?version=stable&style=flat
    :target: https://cedar-backup3.readthedocs.io/en/stable/

Cedar Backup is a software package designed to manage system backups for a pool
of local and remote machines. 

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


Documentation
-------------

See the Changelog_ for recent changes.

The :doc:`manual/index` documents the process of setting up and using Cedar
Backup.  In the manual, you can find information about how Cedar Backup works,
how to install and configure it, how to schedule backups, how to restore data,
and how to get support.


Package Distributions
---------------------

Cedar Backup is primarily distributed as a Python 3 package.  You can install
it using pip::

    $ pip install cedar-backup3

In addition to the Python package, Cedar Backup requires a variety of external 
system dependencies.  For more information, see the :doc:`manual/index`.

Debian packages for Cedar Backup v3, called ``cedar-backup3`` and
``cedar-backup3-doc``, were first available starting with the Debian 'stretch'
release.  Debian derivatives (such as Ubuntu) should also contain the packages.


Library Code
------------

The Cedar Backup v3 has been designed as both an application and a
library of backup-related functionality.  The ``CedarBackup3`` Python package
contains a variety of useful backup-related classes and functions.  For
instance: the ``IsoImage`` class represents an ISO CD image; the ``CdWriter``
class represents a CD-R/CD-RW writer device; and the ``FilesystemList`` class
represents a list of files and directories on a filesystem.  

.. toctree::
   :maxdepth: 1


Contributing Improvements
-------------------------

Users are welcome to contribute improvements to Cedar Backup.  In the past,
users have helped out by reporting unit test failures, making suggestions,
requesting enhancements, updating documentation, submitting patches, and
beta-testing entire releases or individual bug fixes.  As a result, Cedar
Backup has evolved into a much more flexible platform than it would otherwise
have been.


Migrating from Version 2 to Version 3
-------------------------------------

The main difference between Cedar Backup v2 and Cedar Backup v3 is the targeted
Python interpreter.  Cedar Backup v2 was designed for Python 2, while v3 is a
conversion of the original code to Python 3.  Other than that, both versions
are functionally equivalent.  The configuration format is unchanged, and you
can mix-and-match masters and clients of different versions in the same backup
pool.  However, v2 is no longer maintained, so you should convert as soon as
possible.

A major design goal for v3 was to facilitate easy migration testing for users,
by making it possible to install v3 on the same server where v2 was
already in use.  A side effect of this design choice is that all of the
executables, configuration files, and logs changed names in v3.  Where v2 used
``cback``, v3 uses ``cback3``: ``cback3.conf`` instead of ``cback.conf``,
``cback3.log`` instead of ``cback.log``, etc.

So, while migrating from v2 to v3 is relatively straightforward, you will have
to make some changes manually.  You will need to create a new configuration
file (or soft link to the old one), modify your cron jobs to use the new
executable name, etc.  You can migrate one server at a time in your pool with
no ill effects, or even incrementally migrate a single server by using v2 and
v3 on different days of the week or for different parts of the backup.

.. _Changelog: https://github.com/pronovic/cedar-backup3/blob/master/Changelog
