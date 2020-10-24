.. _cedar-recovering:

Data Recovery
=============

.. _cedar-recovering-finding:

Finding your Data
-----------------

The first step in data recovery is finding the data that you want to
recover. You need to decide whether you are going to to restore off
backup media, or out of some existing staging data that has not yet been
purged. The only difference is, if you purge staging data less
frequently than once per week, you might have some data available in the
staging directories which would not be found on your backup media,
depending on how you rotate your media. (And of course, if your system
is trashed or stolen, you probably will not have access to your old
staging data in any case.)

Regardless of the data source you choose, you will find the data
organized in the same way. The remainder of these examples will work off
an example backup disc, but the contents of the staging directory will
look pretty much like the contents of the disc, with data organized
first by date and then by backup peer name.

This is the root directory of my example disc:

::

   root:/mnt/cdrw# ls -l
   total 4
   drwxr-x---  3 backup backup 4096 Sep 01 06:30 2005/
         

In this root directory is one subdirectory for each year represented in
the backup. In this example, the backup represents data entirely from
the year 2005. If your configured backup week happens to span a year
boundary, there would be two subdirectories here (for example, one for
2005 and one for 2006).

Within each year directory is one subdirectory for each month
represented in the backup.

::

   root:/mnt/cdrw/2005# ls -l
   total 2
   dr-xr-xr-x  6 root root 2048 Sep 11 05:30 09/
         

In this example, the backup represents data entirely from the month of
September, 2005. If your configured backup week happens to span a month
boundary, there would be two subdirectories here (for example, one for
August 2005 and one for September 2005).

Within each month directory is one subdirectory for each day represented
in the backup.

::

   root:/mnt/cdrw/2005/09# ls -l
   total 8
   dr-xr-xr-x  5 root root 2048 Sep  7 05:30 07/
   dr-xr-xr-x  5 root root 2048 Sep  8 05:30 08/
   dr-xr-xr-x  5 root root 2048 Sep  9 05:30 09/
   dr-xr-xr-x  5 root root 2048 Sep 11 05:30 11/
         

Depending on how far into the week your backup media is from, you might
have as few as one daily directory in here, or as many as seven.

Within each daily directory is a stage indicator (indicating when the
directory was staged) and one directory for each peer configured in the
backup:

::

   root:/mnt/cdrw/2005/09/07# ls -l
   total 10
   dr-xr-xr-x  2 root root 2048 Sep  7 02:31 host1/
   -r--r--r--  1 root root    0 Sep  7 03:27 cback.stage
   dr-xr-xr-x  2 root root 4096 Sep  7 02:30 host2/
   dr-xr-xr-x  2 root root 4096 Sep  7 03:23 host3/
         

In this case, you can see that my backup includes three machines, and
that the backup data was staged on September 7, 2005 at 03:27.

Within the directory for a given host are all of the files collected on
that host. This might just include tarfiles from a normal Cedar Backup
collect run, and might also include files “collected” from Cedar Backup
extensions or by other third-party processes on your system.

::

   root:/mnt/cdrw/2005/09/07/host1# ls -l
   total 157976
   -r--r--r--  1 root root 11206159 Sep  7 02:30 boot.tar.bz2
   -r--r--r--  1 root root        0 Sep  7 02:30 cback.collect
   -r--r--r--  1 root root     3199 Sep  7 02:30 dpkg-selections.txt.bz2
   -r--r--r--  1 root root   908325 Sep  7 02:30 etc.tar.bz2
   -r--r--r--  1 root root      389 Sep  7 02:30 fdisk-l.txt.bz2
   -r--r--r--  1 root root  1003100 Sep  7 02:30 ls-laR.txt.bz2
   -r--r--r--  1 root root    19800 Sep  7 02:30 mysqldump.txt.bz2
   -r--r--r--  1 root root  4133372 Sep  7 02:30 opt-local.tar.bz2
   -r--r--r--  1 root root 44794124 Sep  8 23:34 opt-public.tar.bz2
   -r--r--r--  1 root root 30028057 Sep  7 02:30 root.tar.bz2
   -r--r--r--  1 root root  4747070 Sep  7 02:30 svndump-0:782-opt-svn-repo1.txt.bz2
   -r--r--r--  1 root root   603863 Sep  7 02:30 svndump-0:136-opt-svn-repo2.txt.bz2
   -r--r--r--  1 root root   113484 Sep  7 02:30 var-lib-jspwiki.tar.bz2
   -r--r--r--  1 root root 19556660 Sep  7 02:30 var-log.tar.bz2
   -r--r--r--  1 root root 14753855 Sep  7 02:30 var-mail.tar.bz2
            

As you can see, I back up variety of different things on host1. I run
the normal collect action, as well as the sysinfo, mysql and subversion
extensions. The resulting backup files are named in a way that makes it
easy to determine what they represent.

Files of the form ``*.tar.bz2`` represent directories backed up by the
collect action. The first part of the name (before “.tar.bz2”),
represents the path to the directory. For example, ``boot.tar.gz``
contains data from ``/boot``, and ``var-lib-jspwiki.tar.bz2`` contains
data from ``/var/lib/jspwiki``.

The ``fdisk-l.txt.bz2``, ``ls-laR.tar.bz2`` and
``dpkg-selections.tar.bz2`` files are produced by the sysinfo extension.

The ``mysqldump.txt.bz2`` file is produced by the mysql extension. It
represents a system-wide database dump, because I use the “all” flag in
configuration. If I were to configure Cedar Backup to dump individual
datbases, then the filename would contain the database name (something
like ``mysqldump-bugs.txt.bz2``).

Finally, the files of the form ``svndump-*.txt.bz2`` are produced by the
subversion extension. There is one dump file for each configured
repository, and the dump file name represents the name of the repository
and the revisions in that dump. So, the file
``svndump-0:782-opt-svn-repo1.txt.bz2`` represents revisions 0-782 of
the repository at ``/opt/svn/repo1``. You can tell that this file
contains a full backup of the repository to this point, because the
starting revision is zero. Later incremental backups would have a
non-zero starting revision, i.e. perhaps 783-785, followed by 786-800,
etc.

.. _cedar-recovering-filesystem:

Recovering Filesystem Data
--------------------------

Filesystem data is gathered by the standard Cedar Backup collect action.
This data is placed into files of the form ``*.tar``. The first part of
the name (before “.tar”), represents the path to the directory. For
example, ``boot.tar`` would contain data from ``/boot``, and
``var-lib-jspwiki.tar`` would contain data from ``/var/lib/jspwiki``.
(As a special case, data from the root directory would be placed in
``-.tar``). Remember that your tarfile might have a bzip2 (``.bz2``) or
gzip (``.gz``) extension, depending on what compression you specified in
configuration.

If you are using full backups every day, the latest backup data is
always within the latest daily directory stored on your backup media or
within your staging directory. If you have some or all of your
directories configured to do incremental backups, then the first day of
the week holds the full backups and the other days represent incremental
differences relative to that first day of the week.

If you are restoring a home directory or some other non-system directory
as part of a full restore, it is probably fine to extract the backup
directly into the filesystem.

If you are restoring a system directory like ``/etc`` as part of a full
restore, extracting directly into the filesystem is likely to break
things, especially if you re-installed a newer version of your operating
system than the one you originally backed up. It's better to extract
directories like this to a temporary location and pick out only the
files you find you need.

When doing a partial restore, I suggest *always* extracting to a
temporary location. Doing it this way gives you more control over what
you restore, and helps you avoid compounding your original problem with
another one (like overwriting the wrong file, oops).

.. _cedar-recovering-filesystem-full:

Full Restore
------------

To do a full system restore, find the newest applicable full backup and
extract it. If you have some incremental backups, extract them into the
same place as the full backup, one by one starting from oldest to
newest. (This way, if a file changed every day you will always get the
latest one.)

All of the backed-up files are stored in the tar file in a relative
fashion, so you can extract from the tar file either directly into the
filesystem, or into a temporary location.

For example, to restore ``boot.tar.bz2`` directly into ``/boot``,
execute ``tar`` from your root directory (``/``):

::

   root:/# bzcat boot.tar.bz2 | tar xvf -
            

Of course, use ``zcat`` or just ``cat``, depending on what kind of
compression is in use.

If you want to extract ``boot.tar.gz`` into a temporary location like
``/tmp/boot`` instead, just change directories first. In this case,
you'd execute the ``tar`` command from within ``/tmp`` instead of ``/``.

::

   root:/tmp# bzcat boot.tar.bz2 | tar xvf -
            

Again, use ``zcat`` or just ``cat`` as appropriate.

For more information, you might want to check out the manpage or GNU
info documentation for the ``tar`` command.

.. _cedar-recovering-filesystem-partial:

Partial Restore
---------------

Most users will need to do a partial restore much more frequently than a
full restore. Perhaps you accidentally removed your home directory, or
forgot to check in some version of a file before deleting it. Or,
perhaps the person who packaged Apache for your system blew away your
web server configuration on upgrade (it happens). The solution to these
and other kinds of problems is a partial restore (assuming you've backed
up the proper things).

The procedure is similar to a full restore. The specific steps depend on
how much information you have about the file you are looking for. Where
with a full restore, you can confidently extract the full backup
followed by each of the incremental backups, this might not be what you
want when doing a partial restore. You may need to take more care in
finding the right version of a file --- since the same file, if
changed frequently, would appear in more than one backup.

Start by finding the backup media that contains the file you are looking
for. If you rotate your backup media, and your last known “contact” with
the file was a while ago, you may need to look on older media to find
it. This may take some effort if you are not sure when the change you
are trying to correct took place.

Once you have decided to look at a particular piece of backup media,
find the correct peer (host), and look for the file in the full backup:

::

   root:/tmp# bzcat boot.tar.bz2 | tar tvf - path/to/file
            

Of course, use ``zcat`` or just ``cat``, depending on what kind of
compression is in use.

The ``tvf`` tells ``tar`` to search for the file in question and just
list the results rather than extracting the file. Note that the filename
is relative (with no starting ``/``). Alternately, you can omit the
``path/to/file`` and search through the output using ``more`` or
``less``

If you haven't found what you are looking for, work your way through the
incremental files for the directory in question. One of them may also
have the file if it changed during the course of the backup. Or, move to
older or newer media and see if you can find the file there.

Once you have found your file, extract it using ``xvf``:

::

   root:/tmp# bzcat boot.tar.bz2 | tar xvf - path/to/file
            

Again, use ``zcat`` or just ``cat`` as appropriate.

Inspect the file and make sure it's what you're looking for. Again, you
may need to move to older or newer media to find the exact version of
your file.

For more information, you might want to check out the manpage or GNU
info documentation for the ``tar`` command.

.. _cedar-recovering-mysql:

Recovering MySQL Data
---------------------

MySQL data is gathered by the Cedar Backup mysql extension. This
extension always creates a full backup each time it runs. This wastes
some space, but makes it easy to restore database data. The following
procedure describes how to restore your MySQL database from the backup.

   |warning|

   I am not a MySQL expert. I am providing this information for
   reference. I have tested these procedures on my own MySQL
   installation; however, I only have a single database for use by
   Bugzilla, and I may have misunderstood something with regard to
   restoring individual databases as a user other than root. If you have
   any doubts, test the procedure below before relying on it!

   MySQL experts and/or knowledgable Cedar Backup users: feel free to
   write me and correct any part of this procedure.

First, find the backup you are interested in. If you have specified “all
databases” in configuration, you will have a single backup file, called
``mysqldump.txt``. If you have specified individual databases in
configuration, then you will have files with names like
``mysqldump-database.txt`` instead. In either case, your file might have
a ``.gz`` or ``.bz2`` extension depending on what kind of compression
you specified in configuration.

If you are restoring an “all databases” backup, make sure that you have
correctly created the root user and know its password. Then, execute:

::

   daystrom:/# bzcat mysqldump.txt.bz2 | mysql -p -u root
         

Of course, use ``zcat`` or just ``cat``, depending on what kind of
compression is in use.

Because the database backup includes ``CREATE DATABASE`` SQL statements, this
command should take care of creating all of the databases within the backup, as
well as populating them.

If you are restoring a backup for a specific database, you have two
choices. If you have a root login, you can use the same command as
above:

::

   daystrom:/# bzcat mysqldump-database.txt.bz2 | mysql -p -u root
         

Otherwise, you can create the database and its login first (or have
someone create it) and then use a database-specific login to execute the
restore:

::

   daystrom:/# bzcat mysqldump-database.txt.bz2 | mysql -p -u user database
         

Again, use ``zcat`` or just ``cat`` as appropriate.

For more information on using MySQL, see the documentation on the MySQL
web site, `<http://mysql.org/>`__, or the manpages for the ``mysql``
and ``mysqldump`` commands.

.. _cedar-recovering-subversion:

Recovering Subversion Data
--------------------------

Subversion data is gathered by the Cedar Backup subversion extension.
Cedar Backup will create either full or incremental backups, but the
procedure for restoring is the same for both. Subversion backups are
always taken on a per-repository basis. If you need to restore more than
one repository, follow the procedures below for each repository you are
interested in.

First, find the backup or backups you are interested in. Typically, you
will need the full backup from the first day of the week and each
incremental backup from the other days of the week.

The subversion extension creates files of the form ``svndump-*.txt``.
These files might have a ``.gz`` or ``.bz2`` extension depending on what
kind of compression you specified in configuration. There is one dump
file for each configured repository, and the dump file name represents
the name of the repository and the revisions in that dump. So, the file
``svndump-0:782-opt-svn-repo1.txt.bz2`` represents revisions 0-782 of
the repository at ``/opt/svn/repo1``. You can tell that this file
contains a full backup of the repository to this point, because the
starting revision is zero. Later incremental backups would have a
non-zero starting revision, i.e. perhaps 783-785, followed by 786-800,
etc.

Next, if you still have the old Subversion repository around, you might
want to just move it off (rename the top-level directory) before
executing the restore. Or, you can restore into a temporary directory
and rename it later to its real name once you've checked it out. That is
what my example below will show.

Next, you need to create a new Subversion repository to hold the
restored data. This example shows an FSFS repository, but that is an
arbitrary choice. You can restore from an FSFS backup into a FSFS
repository or a BDB repository. The Subversion dump format is
“backend-agnostic”.

::

   root:/tmp# svnadmin create --fs-type=fsfs testrepo
         

Next, load the full backup into the repository:

::

   root:/tmp# bzcat svndump-0:782-opt-svn-repo1.txt.bz2 | svnadmin load testrepo
         

Of course, use ``zcat`` or just ``cat``, depending on what kind of
compression is in use.

Follow that with loads for each of the incremental backups:

::

   root:/tmp# bzcat svndump-783:785-opt-svn-repo1.txt.bz2 | svnadmin load testrepo
   root:/tmp# bzcat svndump-786:800-opt-svn-repo1.txt.bz2 | svnadmin load testrepo
         

Again, use ``zcat`` or just ``cat`` as appropriate.

When this is done, your repository will be restored to the point of the
last commit indicated in the svndump file (in this case, to revision
800).

   |note|

   *Note:* don't be surprised if, when you test this, the restored
   directory doesn't have exactly the same contents as the original
   directory. I can't explain why this happens, but if you execute
   ``svnadmin dump`` on both old and new repositories, the results are
   identical. This means that the repositories do contain the same
   content.

For more information on using Subversion, see the book Version Control
with Subversion (`<http://svnbook.red-bean.com/>`__) or the Subversion
FAQ (`<http://subversion.tigris.org/faq.html>`__).

.. _cedar-recovering-mbox:

Recovering Mailbox Data
-----------------------

Mailbox data is gathered by the Cedar Backup mbox extension. Cedar
Backup will create either full or incremental backups, but both kinds of
backups are treated identically when restoring.

Individual mbox files and mbox directories are treated a little
differently, since individual files are just compressed, but directories
are collected into a tar archive.

First, find the backup or backups you are interested in. Typically, you
will need the full backup from the first day of the week and each
incremental backup from the other days of the week.

The mbox extension creates files of the form ``mbox-*``. Backup files
for individual mbox files might have a ``.gz`` or ``.bz2`` extension
depending on what kind of compression you specified in configuration.
Backup files for mbox directories will have a ``.tar``, ``.tar.gz`` or
``.tar.bz2`` extension, again depending on what kind of compression you
specified in configuration.

There is one backup file for each configured mbox file or directory. The
backup file name represents the name of the file or directory and the
date it was backed up. So, the file
``mbox-20060624-home-user-mail-greylist`` represents the backup for
``/home/user/mail/greylist`` run on 24 Jun 2006. Likewise,
``mbox-20060624-home-user-mail.tar`` represents the backup for the
``/home/user/mail`` directory run on that same date.

Once you have found the files you are looking for, the restoration
procedure is fairly simple. First, concatenate all of the backup files
together. Then, use grepmail to eliminate duplicate messages (if any).

Here is an example for a single backed-up file:

::

   root:/tmp# rm restore.mbox # make sure it's not left over
   root:/tmp# cat mbox-20060624-home-user-mail-greylist >> restore.mbox
   root:/tmp# cat mbox-20060625-home-user-mail-greylist >> restore.mbox
   root:/tmp# cat mbox-20060626-home-user-mail-greylist >> restore.mbox
   root:/tmp# grepmail -a -u restore.mbox > nodups.mbox
         

At this point, ``nodups.mbox`` contains all of the backed-up messages
from ``/home/user/mail/greylist``.

Of course, if your backups are compressed, you'll have to use ``zcat``
or ``bzcat`` rather than just ``cat``.

If you are backing up mbox directories rather than individual files, see
the filesystem instructions for notes on now to extract the individual
files from inside tar archives. Extract the files you are interested in,
and then concatenate them together just like shown above for the
individual case.

.. _cedar-recovering-split:

Recovering Data split by the Split Extension
--------------------------------------------

The Split extension takes large files and splits them up into smaller
files. Typically, it would be used in conjunction with the
``cback3-span`` command.

The split up files are not difficult to work with. Simply find all of
the files --- which could be split between multiple discs --- and
concatenate them together.

::

   root:/tmp# rm usr-src-software.tar.gz  # make sure it's not there
   root:/tmp# cat usr-src-software.tar.gz_00001 >> usr-src-software.tar.gz
   root:/tmp# cat usr-src-software.tar.gz_00002 >> usr-src-software.tar.gz
   root:/tmp# cat usr-src-software.tar.gz_00003 >> usr-src-software.tar.gz
         

Then, use the resulting file like usual.

Remember, you need to have *all* of the files that the original large
file was split into before this will work. If you are missing a file,
the result of the concatenation step will be either a corrupt file or a
truncated file (depending on which chunks you did not include).

----------

*Previous*: :doc:`depends` • *Next*: :doc:`securingssh`

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
