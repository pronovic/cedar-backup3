.. _cedar-install:

Installation
============

.. _cedar-install-background:

Background
----------

There are two different ways to install Cedar Backup. The easiest way is
to install the pre-built Debian packages. This method is painless and
ensures that all of the correct dependencies are available, etc.

If you are running a Linux distribution other than Debian or you are running
some other platform like FreeBSD or Mac OS X, then you must install the python
package.  When using the Python package, you need to manage all of the external
dependencies yourself.

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
CD/DVD images. A full list of dependencies is provided further on in
this chapter.

.. _cedar-install-debian:

Installing on a Debian System
-----------------------------

The easiest way to install Cedar Backup onto a Debian system is by using
a tool such as ``apt-get`` or ``aptitude``.

Install Cedar Backup using this set of commands:

::

   $ apt-get update
   $ apt-get install cedar-backup3 cedar-backup3-doc
         

Several of the Cedar Backup dependencies are listed as “recommended” rather
than required. If you are installing Cedar Backup on a master machine, you must
install some or all of the recommended dependencies, depending on which actions
you intend to execute. The stage action normally requires *ssh*, and the store
action requires *eject* and either *cdrecord*/*mkisofs* or *dvd+rw-tools*.
Clients must also install some sort of SSH server if a remote master will
collect backups from them.

Once the package has been installed, you can proceed to configuration as
described in :doc:`config`.

   |note|

   The Debian package-management tools must generally be run as root. It is
   safe to install Cedar Backup to a non-standard location and run it as a
   non-root user. However, to do this, you must install the Python package
   instead of the Debian package.

.. _cedar-install-python:

Installing the Python Package 
-----------------------------

On platforms other than Debian, Cedar Backup is installed as a Python package.
You will have to manage external dependencies on your own.

The easiest way to install the Python package is using Pip::

    $ pip install cedar-backup3

There are other ways to install a package, but this is the simplest and is
probably the mechanism most people will want to use.  If you are an experienced
Python user, feel free to use whichever mechanism you prefer on your own
system.

.. _cedar-install-python-deps:

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup requires a number of external packages in order to function
properly. Before installing Cedar Backup, you must make sure that these
dependencies are met.

Cedar Backup is written in Python 3 and requires version 3.7 or greater
of the language.

Additionally, remote client peer nodes must be running an RSH-compatible
server, such as the ``ssh`` server, and master nodes must have an
RSH-compatible client installed if they need to connect to remote peer
machines.

Master machines also require several other system utilities, most having
to do with writing and validating CD/DVD media. On master machines, you
must make sure that these utilities are available if you want to to run
the store action:

-  ``mkisofs``

-  ``eject``

-  ``mount``

-  ``unmount``

-  ``volname``

Then, you need this utility if you are writing CD media:

-  ``cdrecord``

*or* these utilities if you are writing DVD media:

-  ``growisofs``

All of these utilities are common and are easy to find for almost any
UNIX-like operating system.

   |tip|

   Many UNIX-like distributions provide an automatic or semi-automatic way to
   install packages like the ones Cedar Backup requires (think RPMs for RedHat,
   Gentoo's Portage system, Homebrew for Mac, or the BSD ports system). If you
   are not sure how to install these packages on your system, you might want to
   check out :doc:`depends`. This appendix provides links to “upstream” source
   packages, plus as much information as I have been able to gather about
   packages for non-Debian platforms.

----------

*Previous*: :doc:`basic` • *Next*: :doc:`commandline`

----------

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
