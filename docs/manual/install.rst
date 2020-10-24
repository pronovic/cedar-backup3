.. _cedar-install:

Installation
============

.. _cedar-install-background:

Background
----------

There are two different ways to install Cedar Backup. The easiest way is
to install the pre-built Debian packages. This method is painless and
ensures that all of the correct dependencies are available, etc.

If you are running a Linux distribution other than Debian or you are
running some other platform like FreeBSD or Mac OS X, then you must use
the Python source distribution to install Cedar Backup. When using this
method, you need to manage all of the dependencies yourself.

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

If you are running a Debian release which contains Cedar Backup, you can
use your normal Debian mirror as an APT data source. (The Debian
“jessie” release is the first release to contain Cedar Backup 3.)
Otherwise, you need to install from the Cedar Solutions APT data source.
To do this, add the Cedar Solutions APT data source to your ``/etc/apt/sources.list`` 
file. [1]_

After you have configured the proper APT data source, install Cedar
Backup using this set of commands:

::

   $ apt-get update
   $ apt-get install cedar-backup3 cedar-backup3-doc
         

Several of the Cedar Backup dependencies are listed as “recommended”
rather than required. If you are installing Cedar Backup on a master
machine, you must install some or all of the recommended dependencies,
depending on which actions you intend to execute. The stage action
normally requires ssh, and the store action requires eject and either
cdrecord/mkisofs or dvd+rw-tools. Clients must also install some sort of
ssh server if a remote master will collect backups from them.

If you would prefer, you can also download the ``.deb`` files and
install them by hand with a tool such as ``dpkg``. You can find these
files files in the Cedar Solutions APT source.

In either case, once the package has been installed, you can proceed to
configuration as described in :doc:`config`.

   |note|

   The Debian package-management tools must generally be run as root. It
   is safe to install Cedar Backup to a non-standard location and run it
   as a non-root user. However, to do this, you must install the source
   distribution instead of the Debian package.

.. _cedar-install-source:

Installing from Source
----------------------

On platforms other than Debian, Cedar Backup is installed from a Python
source distribution.  [2]_ You will have to manage dependencies on your
own.

   |tip|

   Many UNIX-like distributions provide an automatic or semi-automatic
   way to install packages like the ones Cedar Backup requires (think
   RPMs for Mandrake or RedHat, Gentoo's Portage system, the Fink
   project for Mac OS X, or the BSD ports system). If you are not sure
   how to install these packages on your system, you might want to check
   out :doc:`depends`. This appendix provides links to
   “upstream” source packages, plus as much information as I have been
   able to gather about packages for non-Debian platforms.

.. _cedar-install-source-deps:

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup requires a number of external packages in order to function
properly. Before installing Cedar Backup, you must make sure that these
dependencies are met.

Cedar Backup is written in Python 3 and requires version 3.4 or greater
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

.. _cedar-install-source-package:

Installing the Source Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python source packages are fairly easy to install. They are distributed
as ``.tar.gz`` files which contain Python source code, a manifest and an
installation script called ``setup.py``.

Once you have downloaded the source package from the Cedar Solutions
website, untar it:

::

   $ zcat CedarBackup3-3.0.0.tar.gz | tar xvf -
            

This will create a directory called (in this case)
``CedarBackup3-3.0.0``. The version number in the directory will always
match the version number in the filename.

If you have root access and want to install the package to the
“standard” Python location on your system, then you can install the
package in two simple steps:

::

   $ cd CedarBackup3-3.0.0
   $ python3 setup.py install
            

Make sure that you are using Python 3.4 or better to execute
``setup.py``.

You may also wish to run the unit tests before actually installing
anything. Run them like so:

::

   python3 util/test.py
            

If any unit test reports a failure on your system, please email me the
output from the unit test, so I can fix the problem.  [3]_ This is
particularly important for non-Linux platforms where I do not have a
test system available to me.

Some users might want to choose a different install location or change
other install parameters. To get more information about how ``setup.py``
works, use the ``--help`` option:

::

   $ python3 setup.py --help
   $ python3 setup.py install --help
            

In any case, once the package has been installed, you can proceed to
configuration as described in :doc:`config`.

----------

*Previous*: :doc:`basic` • *Next*: :doc:`commandline`

----------

.. [1]
   See `<http://cedar-solutions.com/debian.html>`__

.. [2]
   See `<http://docs.python.org/lib/module-distutils.html>`__ .

.. [3]
   support@cedar-solutions.com

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
