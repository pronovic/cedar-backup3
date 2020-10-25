.. _cedar-basic:

Basic Concepts
==============

.. _cedar-basic-general:

General Architecture
--------------------

Cedar Backup is architected as a Python package (library) and a single
executable (a Python script). The Python package provides both
application-specific code and general utilities that can be used by
programs other than Cedar Backup. It also includes modules that can be
used by third parties to extend Cedar Backup or provide related
functionality.

The ``cback3`` script is designed to run as root, since otherwise it's
difficult to back up system directories or write to the CD/DVD device.
However, pains are taken to use the backup user's effective user id
(specified in configuration) when appropriate. *Note:* this does not mean
that ``cback3`` runs setuid [1]_ or setgid. However, all files on disk
will be owned by the backup user, and and all rsh-based network
connections will take place as the backup user.

The ``cback3`` script is configured via command-line options and an XML
configuration file on disk. The configuration file is normally stored in
``/etc/cback3.conf``, but this path can be overridden at runtime. See
:doc:`config` for more information on how Cedar Backup is
configured.

   |warning|

   You should be aware that backups to CD/DVD media can probably be read
   by any user which has permissions to mount the CD/DVD writer. If you
   intend to leave the backup disc in the drive at all times, you may
   want to consider this when setting up device permissions on your
   machine. See also :doc:`extensions`.

.. _cedar-basic-datarecovery:

Data Recovery
-------------

Cedar Backup does not include any facility to restore backups. Instead,
it assumes that the administrator (using the procedures and references
in :doc:`recovering`) can handle the task of restoring their
own system, using the standard system tools at hand.

If I were to maintain recovery code in Cedar Backup, I would almost
certainly end up in one of two situations. Either Cedar Backup would
only support simple recovery tasks, and those via an interface a lot
like that of the underlying system tools; or Cedar Backup would have to
include a hugely complicated interface to support more specialized (and
hence useful) recovery tasks like restoring individual files as of a
certain point in time. In either case, I would end up trying to maintain
critical functionality that would be rarely used, and hence would also
be rarely tested by end-users. I am uncomfortable asking anyone to rely
on functionality that falls into this category.

My primary goal is to keep the Cedar Backup codebase as simple and
focused as possible. I hope you can understand how the choice of
providing documentation, but not code, seems to strike the best balance
between managing code complexity and providing the functionality that
end-users need.

.. _cedar-basic-pools:

Cedar Backup Pools
-------------------

There are two kinds of machines in a Cedar Backup pool. One machine (the
*master*) has a CD or DVD writer on it and writes the backup to disc.  If you are
using Amazon S3 instead of physical media, then the master is the machine that
consolidates data and writes your backup to cloud storage.  The other machines
(*clients*) collect data to be written to disc by the master.  Collectively, the
master and client machines in a pool are called *peer machines*.

Cedar Backup has been designed primarily for situations where there is a single
master and a set of other clients that the master interacts with.  However, it
will just as easily work for a single machine (a backup pool of one) and in
fact more users seem to use it like this than any other way.

.. _cedar-basic-process:

The Backup Process
------------------

The Cedar Backup backup process is structured in terms of a set of
decoupled actions which execute independently (based on a schedule in
``cron``) rather than through some highly coordinated flow of control.

This design decision has both positive and negative consequences. On the
one hand, the code is much simpler and can choose to simply abort or log
an error if its expectations are not met. On the other hand, the
administrator must coordinate the various actions during initial set-up.
See *Coordination between Master and Clients* (later in this chapter) for more
information on this subject.

A standard backup run consists of four steps (actions), some of which
execute on the master machine, and some of which execute on one or more
client machines. These actions are: collect, stage, store and purge.

In general, more than one action may be specified on the command-line.  If more
than one action is specified, then actions will be taken in a sensible order
(generally *collect*, *stage*, *store*, *purge*). A special *all* action is
also allowed, which implies all of the standard actions in the same sensible
order.

The ``cback3`` command also supports several actions that are not part of the
standard backup run and cannot be executed along with any other actions. These
actions are *validate*, *initialize* and *rebuild*. All of the various actions
are discussed further below.

See :doc:`config` for more information on how a backup run is
configured.

Cedar Backup was designed to be flexible. It allows you to decide for
yourself which backup steps you care about executing (and when you
execute them), based on your own situation and your own priorities.

For example, no need to write to disc or to Amazon S3 at all. In fact, some
users prefer to use their master machine as a simple “consolidation point”.
They don't back up any data on the master, and don't write to disc at all. They
just use Cedar Backup to handle the mechanics of moving backed-up data to a
central location. This isn't quite what Cedar Backup was written to do, but it
is flexible enough to meet their needs.

.. _cedar-basic-process-collect:

The Collect Action
~~~~~~~~~~~~~~~~~~

The collect action is the first action in a standard backup run. It
executes on both master and client nodes. Based on configuration, this
action traverses the peer's filesystem and gathers files to be backed
up. Each configured high-level directory is collected up into its own
``tar`` file in the collect directory. The tarfiles can either be
uncompressed (``.tar``) or compressed with either ``gzip`` (``.tar.gz``)
or ``bzip2`` (``.tar.bz2``).

There are three supported collect modes: *daily*, *weekly* and *incremental*.
Directories configured for daily backups are backed up every day.
Directories configured for weekly backups are backed up on the first day
of the week. Directories configured for incremental backups are
traversed every day, but only the files which have changed (based on a
saved-off cryptographic hash) are actually backed up.

Collect configuration also allows for a variety of ways to filter files and
directories out of the backup. For instance, administrators can configure an
ignore indicator file or specify absolute paths or filename patterns to be
excluded. You can even configure a backup “link farm” rather than explicitly
listing files and directories in configuration.

This action is optional on the master. You only need to configure and
execute the collect action on the master if you have data to back up on
that machine. If you plan to use the master only as a “consolidation
point” to collect data from other machines, then there is no need to
execute the collect action there. If you run the collect action on the
master, it behaves the same there as anywhere else, and you have to
stage the master's collected data just like any other client (typically
by configuring a local peer in the stage action).

.. _cedar-basic-process-stage:

The Stage Action
~~~~~~~~~~~~~~~~

The stage action is the second action in a standard backup run. It
executes on the master peer node. The master works down the list of
peers in its backup pool and stages (copies) the collected backup files
from each of them into a daily staging directory by peer name.

For the purposes of this action, the master node can be configured to
treat itself as a client node. If you intend to back up data on the
master, configure the master as a local peer. Otherwise, just configure
each of the clients as a remote peer.

Local and remote client peers are treated differently. Local peer
collect directories are assumed to be accessible via normal copy
commands (i.e. on a mounted filesystem) while remote peer collect
directories are accessed via an RSH-compatible command such as ``ssh``.

If a given peer is not ready to be staged, the stage process will log an
error, abort the backup for that peer, and then move on to its other
peers. This way, one broken peer cannot break a backup for other peers
which are up and running.

Keep in mind that Cedar Backup is flexible about what actions must be
executed as part of a backup. If you would prefer, you can stop the
backup process at this step, and skip the store step. In this case, the
staged directories will represent your backup rather than a disc or
an Amazon S3 bucket.

   |note|

   Directories “collected” by another process can alsoalso  be staged by Cedar
   Backup. If the file ``cback.collect`` exists in a collect directory
   when the stage action is taken, then that directory will be staged.

.. _cedar-basic-process-store:

The Store Action
~~~~~~~~~~~~~~~~

The store action is the third action in a standard backup run. It
executes on the master peer node. The master machine determines the
location of the current staging directory, and then writes the contents
of that staging directory to disc. After the contents of the directory
have been written to disc, an optional validation step ensures that the
write was successful.

If the backup is running on the first day of the week, if the drive does
not support multisession discs, or if the ``--full`` option is passed to
the ``cback3`` command, the disc will be rebuilt from scratch.
Otherwise, a new ISO session will be added to the disc each day the
backup runs.

This action is entirely optional. If you would prefer to just stage
backup data from a set of peers to a master machine, and have the staged
directories represent your backup rather than a disc, this is fine.

   |warning|

   The store action is not supported on the Mac OS X (darwin) platform.
   On that platform, the “automount” function of the Finder interferes
   significantly with Cedar Backup's ability to mount and unmount media
   and write to the CD or DVD hardware. The Cedar Backup writer and
   image functionality works on this platform, but the effort required
   to fight the operating system about who owns the media and the device
   makes it nearly impossible to execute the store action successfully.

The store action tries to be smart about finding the current staging
directory. It first checks the current day's staging directory. If that
directory exists, and it has not yet been written to disc (i.e. there is
no store indicator), then it will be used. Otherwise, the store action
will look for an unused staging directory for either the previous day or
the next day, in that order. A warning will be written to the log under
these circumstances (controlled by the ``<warn_midnite>`` configuration
value).

This behavior varies slightly when the ``--full`` option is in effect.
Under these circumstances, any existing store indicator will be ignored.
Also, the store action will always attempt to use the current day's
staging directory, ignoring any staging directories for the previous day
or the next day. This way, running a full store action more than once
concurrently will always produce the same results. (You might imagine a
use case where a person wants to make several copies of the same full
backup.)

.. _cedar-basic-process-purge:

The Purge Action
~~~~~~~~~~~~~~~~

The purge action is the fourth and final action in a standard backup
run. It executes both on the master and client peer nodes. Configuration
specifies how long to retain files in certain directories, and older
files and empty directories are purged.

Typically, collect directories are purged daily, and stage directories
are purged weekly or slightly less often (if a disc gets corrupted,
older backups may still be available on the master). Some users also
choose to purge the configured working directory (which is used for
temporary files) to eliminate any leftover files which might have
resulted from changes to configuration.

.. _cedar-basic-process-all:

The All Action
~~~~~~~~~~~~~~

The all action is a pseudo-action which causes all of the actions in a
standard backup run to be executed together in order. It cannot be
combined with any other actions on the command line.

Extensions *cannot* be executed as part of the all action. If you need
to execute an extended action, you must specify the other actions you
want to run individually on the command line.  [2]_

The all action does not have its own configuration. Instead, it relies
on the individual configuration sections for all of the other actions.

.. _cedar-basic-process-validate:

The Validate Action
~~~~~~~~~~~~~~~~~~~

The validate action is used to validate configuration on a particular
peer node, either master or client. It cannot be combined with any other
actions on the command line.

The validate action checks that the configuration file can be found,
that the configuration file is valid, and that certain portions of the
configuration file make sense (for instance, making sure that specified
users exist, directories are readable and writable as necessary, etc.).

.. _cedar-basic-process-initialize:

The Initialize Action
~~~~~~~~~~~~~~~~~~~~~

The initialize action is used to initialize media for use with Cedar
Backup. This is an optional step. By default, Cedar Backup does not need
to use initialized media and will write to whatever media exists in the
writer device.

However, if the “check media” store configuration option is set to true,
Cedar Backup will check the media before writing to it and will error
out if the media has not been initialized.

Initializing the media consists of writing a mostly-empty image using a
known media label (the media label will begin with “CEDAR BACKUP”).

Note that only rewritable media (CD-RW, DVD+RW) can be initialized. It
doesn't make any sense to initialize media that cannot be rewritten
(CD-R, DVD+R), since Cedar Backup would then not be able to use that
media for a backup. You can still configure Cedar Backup to check
non-rewritable media; in this case, the check will also pass if the
media is apparently unused (i.e. has no media label).

.. _cedar-basic-process-rebuild:

The Rebuild Action
~~~~~~~~~~~~~~~~~~

The rebuild action is an exception-handling action that is executed
independent of a standard backup run. It cannot be combined with any
other actions on the command line.

The rebuild action attempts to rebuild “this week's” disc from any
remaining unpurged staging directories. Typically, it is used to make a
copy of a backup, replace lost or damaged media, or to switch to new
media mid-week for some other reason.

To decide what data to write to disc again, the rebuild action looks
back and finds the first day of the current week. Then, it finds any
remaining staging directories between that date and the current date. If
any staging directories are found, they are all written to disc in one
big ISO session.

The rebuild action does not have its own configuration. It relies on
configuration for other other actions, especially the store action.

.. _cedar-basic-coordinate:

Coordination between Master and Clients
---------------------------------------

Unless you are using Cedar Backup to manage a “pool of one”, you will
need to set up some coordination between your clients and master to make
everything work properly. This coordination isn't difficult --- it
mostly consists of making sure that operations happen in the right order
--- but some users are suprised that it is required and want to know
why Cedar Backup can't just “take care of it for me”.

Essentially, each client must finish collecting all of its data before
the master begins staging it, and the master must finish staging data
from a client before that client purges its collected data.
Administrators may need to experiment with the time between the collect
and purge entries so that the master has enough time to stage data
before it is purged.

.. _cedar-basic-managedbackups:

Managed Backups
---------------

Cedar Backup also supports an optional feature called the “managed
backup”. This feature is intended for use with remote clients where cron
is not available.

When managed backups are enabled, managed clients must still be
configured as usual. However, rather than using a cron job on the client
to execute the collect and purge actions, the master executes these
actions on the client via a remote shell.

To make this happen, first set up one or more managed clients in Cedar
Backup configuration. Then, invoke Cedar Backup with the ``--managed``
command-line option. Whenever Cedar Backup invokes an action locally, it
will invoke the same action on each of the managed clients.

Technically, this feature works for any client, not just clients that
don't have cron available. Used this way, it can simplify the setup
process, because cron only has to be configured on the master. For some
users, that may be motivation enough to use this feature all of the
time.

However, please keep in mind that this feature depends on a stable
network. If your network connection drops, your backup will be
interrupted and will not be complete. It is even possible that some of
the Cedar Backup metadata (like incremental backup state) will be
corrupted. The risk is not high, but it is something you need to be
aware of if you choose to use this optional feature.

.. _cedar-basic-mediadevice:

Media and Device Types
----------------------

Cedar Backup is focused around writing backups to CD or DVD media using
a standard SCSI or IDE writer. In Cedar Backup terms, the disc itself is
referred to as the media, and the CD/DVD drive is referred to as the
device or sometimes the backup device.

When using a new enough backup device, a new “multisession” ISO image [3]_ 
is written to the media on the first day of the week, and then additional
multisession images are added to the media each day that Cedar Backup runs.
This way, the media is complete and usable at the end of every backup run, but
a single disc can be used all week long. If your backup device does not support
multisession images --- which is really unusual today --- then a new ISO image
will be written to the media each time Cedar Backup runs (and you should
probably confine yourself to the “daily” backup mode to avoid losing data).

Cedar Backup currently supports four different kinds of CD media:

cdr-74
   74-minute non-rewritable CD media

cdrw-74
   74-minute rewritable CD media

cdr-80
   80-minute non-rewritable CD media

cdrw-80
   80-minute rewritable CD media

I have chosen to support just these four types of CD media because they
seem to be the most “standard” of the various types commonly sold in the
U.S. as of this writing (early 2005). If you regularly use an
unsupported media type and would like Cedar Backup to support it, send
me information about the capacity of the media in megabytes (MB) and
whether it is rewritable.

Cedar Backup also supports two kinds of DVD media:

dvd+r
   Single-layer non-rewritable DVD+R media

dvd+rw
   Single-layer rewritable DVD+RW media

The underlying ``growisofs`` utility does support other kinds of media
(including DVD-R, DVD-RW and BlueRay) which work somewhat differently
than standard DVD+R and DVD+RW media. I don't support these other kinds
of media because I haven't had any opportunity to work with them. The
same goes for dual-layer media of any type.

.. _cedar-basic-incremental:

Incremental Backups
-------------------

Cedar Backup supports three different kinds of backups for individual
collect directories. These are daily, weekly and incremental backups.
Directories using the daily mode are backed up every day. Directories
using the weekly mode are only backed up on the first day of the week,
or when the ``--full`` option is used. Directories using the incremental
mode are always backed up on the first day of the week (like a weekly
backup), but after that only the files which have changed are actually
backed up on a daily basis.

In Cedar Backup, incremental backups are not based on date, but are
instead based on saved checksums, one for each backed-up file. When a
full backup is run, Cedar Backup gathers a checksum value  [4]_ for each
backed-up file. The next time an incremental backup is run, Cedar Backup
checks its list of file/checksum pairs for each file that might be
backed up. If the file's checksum value does not match the saved value,
or if the file does not appear in the list of file/checksum pairs, then
it will be backed up and a new checksum value will be placed into the
list. Otherwise, the file will be ignored and the checksum value will be
left unchanged.

Cedar Backup stores the file/checksum pairs in ``.sha`` files in its
working directory, one file per configured collect directory. The
mappings in these files are reset at the start of the week or when the
``--full`` option is used. Because these files are used for an entire
week, you should never purge the working directory more frequently than
once per week.

.. _cedar-basic-extensions:

Extensions
----------

Imagine that there is a third party developer who understands how to
back up a certain kind of database repository. This third party might
want to integrate his or her specialized backup into the Cedar Backup
process, perhaps thinking of the database backup as a sort of “collect”
step.

Prior to Cedar Backup version 2, any such integration would have been
completely independent of Cedar Backup itself. The “external” backup
functionality would have had to maintain its own configuration and would
not have had access to any Cedar Backup configuration.

Starting with version 2, Cedar Backup allows extensions to the backup
process. An extension is an action that isn't part of the standard
backup process (i.e. not collect, stage, store or purge), but can be
executed by Cedar Backup when properly configured.

Extension authors implement an “action process” function with a certain
interface, and are allowed to add their own sections to the Cedar Backup
configuration file, so that all backup configuration can be centralized.
Then, the action process function is associated with an action name
which can be executed from the ``cback3`` command line like any other
action.

Hopefully, as the Cedar Backup user community grows, users will
contribute their own extensions back to the community. Well-written
general-purpose extensions will be accepted into the official codebase.

   |note|

   See :doc:`config` for more information on how
   extensions are configured, and :doc:`extensions` for
   details on all of the officially-supported extensions.

   Developers may be interested in :doc:`extenspec`.

----------

*Previous*: :doc:`preface` • *Next*: :doc:`install`

----------

.. [1]
   See `<http://en.wikipedia.org/wiki/Setuid>`__

.. [2]
   Some users find this surprising, because extensions are configured
   with sequence numbers. I did it this way because I felt that running
   extensions as part of the all action would sometimes result in
   surprising behavior. I am not planning to change the way this works.

.. [3]
   An ISO image is the standard way of creating a filesystem to be
   copied to a CD or DVD. It is essentially a “filesystem-within-a-file”
   and many UNIX operating systems can actually mount ISO image files
   just like hard drives, floppy disks or actual CDs. See Wikipedia for
   more information: `<http://en.wikipedia.org/wiki/ISO_image>`__.

.. [4]
   The checksum is actually an SHA cryptographic hash. See Wikipedia for
   more information: `<http://en.wikipedia.org/wiki/SHA-1>`__.

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
