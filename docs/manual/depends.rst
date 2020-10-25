.. _cedar-depends:

Dependencies
============

Python 3.7 (or later)

   +---------------+------------------------------------------------------------------+
   | Source        | URL                                                              |
   +===============+==================================================================+
   | upstream      | `<http://www.python.org>`__                                      |
   +---------------+------------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/python/python3>`__           |
   +---------------+------------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=python3>`__ |
   +---------------+------------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

RSH Server and Client

   Although Cedar Backup will technically work with any RSH-compatible
   server and client pair (such as the classic “rsh” client), most users
   should only use an SSH (secure shell) server and client.

   The defacto standard today is OpenSSH. Some systems package the
   server and the client together, and others package the server and the
   client separately. Note that master nodes need an SSH client, and
   client nodes need to run an SSH server.

   +---------------+------------------------------------------------------------------+
   | Source        | URL                                                              |
   +===============+==================================================================+
   | upstream      | `<http://www.openssh.com/>`__                                    |
   +---------------+------------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/net/ssh>`__                  |
   +---------------+------------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=openssh>`__ |
   +---------------+------------------------------------------------------------------+

   If you can't find SSH client or server packages for your system,
   install from the package source, using the “upstream” link.

``mkisofs``

   The ``mkisofs`` command is used create ISO filesystem images that can
   later be written to backup media.

   On Debian platforms, ``mkisofs`` is not distributed and
   ``genisoimage`` is used instead. The Debian package takes care of
   this for you.

   +---------------+-------------------------------------------------------------------+
   | Source        | URL                                                               |
   +===============+===================================================================+
   | upstream      | `<https://en.wikipedia.org/wiki/Cdrtools>`__                      |
   +---------------+-------------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=mkisofs>`__  |
   +---------------+-------------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``cdrecord``

   The ``cdrecord`` command is used to write ISO images to CD media in a
   backup device.

   On Debian platforms, ``cdrecord`` is not distributed and ``wodim`` is
   used instead. The Debian package takes care of this for you.

   +---------------+-------------------------------------------------------------------+
   | Source        | URL                                                               |
   +===============+===================================================================+
   | upstream      | `<https://en.wikipedia.org/wiki/Cdrtools>`__                      |
   +---------------+-------------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=cdrecord>`__ |
   +---------------+-------------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``dvd+rw-tools``

   The dvd+rw-tools package provides the ``growisofs`` utility, which is
   used to write ISO images to DVD media in a backup device.

   +---------------+-----------------------------------------------------------------------+
   | Source        | URL                                                                   |
   +===============+=======================================================================+
   | upstream      | `<http://fy.chalmers.se/~appro/linux/DVD+RW/>`__                      |
   +---------------+-----------------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/utils/dvd+rw-tools>`__            |
   +---------------+-----------------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=dvd+rw-tools>`__ |
   +---------------+-----------------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``eject`` and ``volname``

   The ``eject`` command is used to open and close the tray on a backup
   device (if the backup device has a tray). Sometimes, the tray must be
   opened and closed in order to "reset" the device so it notices recent
   changes to a disc.

   The ``volname`` command is used to determine the volume name of media
   in a backup device.

   +---------------+-----------------------------------------------------------------+
   | Source        | URL                                                             |
   +===============+=================================================================+
   | upstream      | `<http://sourceforge.net/projects/eject>`__                     |
   +---------------+-----------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/utils/eject>`__             |
   +---------------+-----------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=eject>`__  |
   +---------------+-----------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``mount`` and ``umount``

   The ``mount`` and ``umount`` commands are used to mount and unmount
   CD/DVD media after it has been written, in order to run a consistency
   check.

   +---------------+----------------------------------------------------------------+
   | Source        | URL                                                            |
   +===============+================================================================+
   | upstream      | `<https://www.kernel.org/pub/linux/utils/util-linux/>`__       |
   +---------------+----------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/base/mount>`__             |
   +---------------+----------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=mount>`__ |
   +---------------+----------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``grepmail``

   The ``grepmail`` command is used by the mbox extension to pull out
   only recent messages from mbox mail folders.

   +---------------+--------------------------------------------------------------------+
   | Source        | URL                                                                |
   +===============+====================================================================+
   | upstream      | `<https://github.com/coppit/grepmail>`__                           |
   +---------------+--------------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/mail/grepmail>`__              |
   +---------------+--------------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=grepmail>`__  |
   +---------------+--------------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``gpg``

   The ``gpg`` command is used by the encrypt extension to encrypt
   files.

   +---------------+-----------------------------------------------------------------+
   | Source        | URL                                                             |
   +===============+=================================================================+
   | upstream      | `<https://www.gnupg.org/>`__                                    |
   +---------------+-----------------------------------------------------------------+
   | Debian        | `<http://packages.debian.org/stable/utils/gnupg>`__             |
   +---------------+-----------------------------------------------------------------+
   | RPM           | `<http://rpmfind.net/linux/rpm2html/search.php?query=gnupg>`__  |
   +---------------+-----------------------------------------------------------------+

   If you can't find a package for your system, install from the package
   source, using the “upstream” link.

``split``

   The ``split`` command is used by the split extension to split up
   large files.

   This command is typically part of the core operating system install
   and is not distributed in a separate package.

``AWS CLI``

   AWS CLI is Amazon's official command-line tool for interacting with
   the Amazon Web Services infrastruture. Cedar Backup uses AWS CLI to
   copy backup data up to Amazon S3 cloud storage.

   After you install AWS CLI, you need to configure your connection to
   AWS with an appropriate access id and access key. Amazon provides a
   good `setup guide <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html>`__.

   +---------------+-------------------------------------------------------+
   | Source        | URL                                                   |
   +===============+=======================================================+
   | upstream      | `<http://aws.amazon.com/documentation/cli/>`__        |
   +---------------+-------------------------------------------------------+
   | Debian        | `<https://packages.debian.org/stable/awscli>`__       |
   +---------------+-------------------------------------------------------+

   The initial implementation of the amazons3 extension was written
   using AWS CLI 1.4. As of this writing, not all Linux distributions
   include a package for this version. On these platforms, the easiest
   way to install it is via PIP: ``apt-get install python3-pip``, and
   then ``pip3 install awscli``. The Debian package includes an
   appropriate dependency starting with the jessie release.

----------

*Previous*: :doc:`extenspec` • *Next*: :doc:`recovering`

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
