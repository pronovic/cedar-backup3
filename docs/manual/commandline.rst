.. _cedar-commandline:

Command Line Tools
==================

.. _cedar-commandline-overview:

Overview
--------

Cedar Backup comes with three command-line programs: ``cback3``,
``cback3-amazons3-sync``, and ``cback3-span``.

The ``cback3`` command is the primary command line interface and the
only Cedar Backup program that most users will ever need.

The ``cback3-amazons3-sync`` tool is used for synchronizing entire
directories of files up to an Amazon S3 cloud storage bucket, outside of
the normal Cedar Backup process.

Users who have a *lot* of data to back up --- more than will fit on a
single CD or DVD --- can use the interactive ``cback3-span`` tool to
split their data between multiple discs.

.. _cedar-commandline-cback3:

The ``cback3`` command
----------------------

.. _cedar-commandline-cback3-intro:

Introduction
~~~~~~~~~~~~

Cedar Backup's primary command-line interface is the ``cback3`` command.
It controls the entire backup process.

.. _cedar-commandline-cback3-syntax:

Syntax
~~~~~~

The ``cback3`` command has the following syntax:

::

    Usage: cback3 [switches] action(s)

    The following switches are accepted:

      -h, --help         Display this usage/help listing
      -V, --version      Display version information
      -b, --verbose      Print verbose output as well as logging to disk
      -q, --quiet        Run quietly (display no output to the screen)
      -c, --config       Path to config file (default: /etc/cback3.conf)
      -f, --full         Perform a full backup, regardless of configuration
      -M, --managed      Include managed clients when executing actions
      -N, --managed-only Include ONLY managed clients when executing actions
      -l, --logfile      Path to logfile (default: /var/log/cback3.log)
      -o, --owner        Logfile ownership, user:group (default: root:adm)
      -m, --mode         Octal logfile permissions mode (default: 640)
      -O, --output       Record some sub-command (i.e. cdrecord) output to the log
      -d, --debug        Write debugging information to the log (implies --output)
      -s, --stack        Dump a Python stack trace instead of swallowing exceptions
      -D, --diagnostics  Print runtime diagnostics to the screen and exit

    The following actions may be specified:

      all                Take all normal actions (collect, stage, store, purge)
      collect            Take the collect action
      stage              Take the stage action
      store              Take the store action
      purge              Take the purge action
      rebuild            Rebuild "this week's" disc if possible
      validate           Validate configuration only
      initialize         Initialize media for use with Cedar Backup

    You may also specify extended actions that have been defined in
    configuration.

    You must specify at least one action to take.  More than one of
    the "collect", "stage", "store" or "purge" actions and/or
    extended actions may be specified in any arbitrary order; they
    will be executed in a sensible order.  The "all", "rebuild",
    "validate", and "initialize" actions may not be combined with
    other actions.
            

Note that the all action *only* executes the standard four actions. It
never executes any of the configured extensions.  [1]_

.. _cedar-commandline-cback3-options:

Switches
~~~~~~~~

``-h``, ``--help``
   Display usage/help listing.

``-V``, ``--version``
   Display version information.

``-b``, ``--verbose``
   Print verbose output to the screen as well writing to the logfile.
   When this option is enabled, most information that would normally be
   written to the logfile will also be written to the screen.

``-q``, ``--quiet``
   Run quietly (display no output to the screen).

``-c``, ``--config``
   Specify the path to an alternate configuration file. The default
   configuration file is ``/etc/cback3.conf``.

``-f``, ``--full``
   Perform a full backup, regardless of configuration. For the collect
   action, this means that any existing information related to
   incremental backups will be ignored and rewritten; for the store
   action, this means that a new disc will be started.

``-M``, ``--managed``
   Include managed clients when executing actions. If the action being
   executed is listed as a managed action for a managed client, execute
   the action on that client after executing the action locally.

``-N``, ``--managed-only``
   Include *only* managed clients when executing actions. If the action
   being executed is listed as a managed action for a managed client,
   execute the action on that client --- but *do not* execute the
   action locally.

``-l``, ``--logfile``
   Specify the path to an alternate logfile. The default logfile file is
   ``/var/log/cback3.log``.

``-o``, ``--owner``
   Specify the ownership of the logfile, in the form ``user:group``. The
   default ownership is ``root:adm``, to match the Debian standard for
   most logfiles. This value will only be used when creating a new
   logfile. If the logfile already exists when the ``cback3`` command is
   executed, it will retain its existing ownership and mode. Only user
   and group names may be used, not numeric uid and gid values.

``-m``, ``--mode``
   Specify the permissions for the logfile, using the numeric mode as in
   ``chmod(1)``. The default mode is ``0640`` (``-rw-r-----``). This value
   will only be used when creating a new logfile. If the logfile already
   exists when the ``cback3`` command is executed, it will retain its
   existing ownership and mode.

``-O``, ``--output``
   Record some sub-command output to the logfile. When this option is
   enabled, all output from system commands will be logged. This might
   be useful for debugging or just for reference.

``-d``, ``--debug``
   Write debugging information to the logfile. This option produces a
   high volume of output, and would generally only be needed when
   debugging a problem. This option implies the ``--output`` option, as
   well.

``-s``, ``--stack``
   Dump a Python stack trace instead of swallowing exceptions. This
   forces Cedar Backup to dump the entire Python stack trace associated
   with an error, rather than just propagating last message it received
   back up to the user interface. Under some circumstances, this is
   useful information to include along with a bug report.

``-D``, ``--diagnostics``
   Display runtime diagnostic information and then exit. This diagnostic
   information is often useful when filing a bug report.

.. _cedar-commandline-cback3-actions:

Actions
~~~~~~~

You can find more information about the various actions in :doc:`basic`. In
general, you may specify any combination of the *collect*, *stage*,
*store* or *purge* actions, and the specified actions will be executed in a
sensible order. Or, you can specify one of the *all*, *rebuild*,
*validate*, or *initialize* actions (but these actions may not be combined
with other actions).

If you have configured any Cedar Backup extensions, then the actions
associated with those extensions may also be specified on the command
line. If you specify any other actions along with an extended action,
the actions will be executed in a sensible order per configuration. The
*all* action never executes extended actions, however.

.. _cedar-commandline-sync:

The ``cback3-amazons3-sync`` command
------------------------------------

.. _cedar-commandline-sync-intro:

Introduction
~~~~~~~~~~~~

The ``cback3-amazons3-sync`` tool is used for synchronizing entire
directories of files up to an Amazon S3 cloud storage bucket, outside of
the normal Cedar Backup process.

This might be a good option for some types of data, as long as you
understand the limitations around retrieving previous versions of
objects that get modified or deleted as part of a sync. S3 does support
versioning, but it won't be quite as easy to get at those previous
versions as with an explicit incremental backup like ``cback3``
provides. Cedar Backup does not provide any tooling that would help you
retrieve previous versions.

The underlying functionality relies on the `AWS CLI <http://aws.amazon.com/documentation/cli/>`__ 
toolset. Before you use this extension, you need to set up your Amazon S3
account and configure AWS CLI as detailed in Amazon's 
`setup guide <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html>`__.
The ``aws`` command will be executed as the same user that is executing
the ``cback3-amazons3-sync`` command, so make sure you configure it as
the proper user. (This is different than the amazons3 extension, which
is designed to execute as root and switches over to the configured
backup user to execute AWS CLI commands.)

.. _cedar-commandline-sync-permissions:

Permissons
~~~~~~~~~~

You can use whichever Amazon-supported authentication mechanism you
would like when setting up connectivity for the AWS CLI. It's best to
set up a separate user in the `IAM Console <https://console.aws.amazon.com/iam/home>`__ 
rather than using your main administrative user.

You probably want to lock down this user so that it can only take backup
related actions in the AWS infrastructure. One option is to apply the
``AmazonS3FullAccess`` policy, which grants full access to the S3
infrastructure. If you would like to lock down the user even further,
this appears to be the minimum set of permissions required for the
``aws s3 sync`` action, written as a JSON policy statement:

::

   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:ListBucket",
                   "s3:PutObject",
                   "s3:PutObjectAcl",
                   "s3:DeleteObject"
               ],
               "Resource": [
                   "arn:aws:s3:::your-bucket",
                   "arn:aws:s3:::your-bucket/*"
               ]
           }
       ]
   } 
               

In the ``Resource`` section, be sure to list the name of your S3 bucket
instead of ``my-bucket``.

.. _cedar-commandline-sync-syntax:

Syntax
~~~~~~

The ``cback3-amazons3-sync`` command has the following syntax:

::

    Usage: cback3-amazons3-sync [switches] sourceDir s3bucketUrl

    Cedar Backup Amazon S3 sync tool.

    This Cedar Backup utility synchronizes a local directory to an Amazon S3
    bucket.  After the sync is complete, a validation step is taken.  An
    error is reported if the contents of the bucket do not match the
    source directory, or if the indicated size for any file differs.
    This tool is a wrapper over the AWS CLI command-line tool.

    The following arguments are required:

      sourceDir            The local source directory on disk (must exist)
      s3BucketUrl          The URL to the target Amazon S3 bucket

    The following switches are accepted:

      -h, --help           Display this usage/help listing
      -V, --version        Display version information
      -b, --verbose        Print verbose output as well as logging to disk
      -q, --quiet          Run quietly (display no output to the screen)
      -l, --logfile        Path to logfile (default: /var/log/cback3.log)
      -o, --owner          Logfile ownership, user:group (default: root:adm)
      -m, --mode           Octal logfile permissions mode (default: 640)
      -O, --output         Record some sub-command (i.e. aws) output to the log
      -d, --debug          Write debugging information to the log (implies --output)
      -s, --stack          Dump Python stack trace instead of swallowing exceptions
      -D, --diagnostics    Print runtime diagnostics to the screen and exit
      -v, --verifyOnly     Only verify the S3 bucket contents, do not make changes
      -v, --uploadOnly     Only upload new data, do not remove files in the S3 bucket
      -w, --ignoreWarnings Ignore warnings about problematic filename encodings

    Typical usage would be something like:

      cback3-amazons3-sync /home/myuser s3://example.com-backup/myuser

    This will sync the contents of /home/myuser into the indicated bucket.
            

.. _cedar-commandline-sync-options:

Switches
~~~~~~~~

``-h``, ``--help``
   Display usage/help listing.

``-V``, ``--version``
   Display version information.

``-b``, ``--verbose``
   Print verbose output to the screen as well writing to the logfile.
   When this option is enabled, most information that would normally be
   written to the logfile will also be written to the screen.

``-q``, ``--quiet``
   Run quietly (display no output to the screen).

``-l``, ``--logfile``
   Specify the path to an alternate logfile. The default logfile file is
   ``/var/log/cback3.log``.

``-o``, ``--owner``
   Specify the ownership of the logfile, in the form ``user:group``. The
   default ownership is ``root:adm``, to match the Debian standard for
   most logfiles. This value will only be used when creating a new
   logfile. If the logfile already exists when the
   ``cback3-amazons3-sync`` command is executed, it will retain its
   existing ownership and mode. Only user and group names may be used,
   not numeric uid and gid values.

``-m``, ``--mode``
   Specify the permissions for the logfile, using the numeric mode as in
   ``chmod(1)``. The default mode is ``0640`` (``-rw-r-----``). This value
   will only be used when creating a new logfile. If the logfile already
   exists when the ``cback3-amazons3-sync`` command is executed, it will
   retain its existing ownership and mode.

``-O``, ``--output``
   Record some sub-command output to the logfile. When this option is
   enabled, all output from system commands will be logged. This might
   be useful for debugging or just for reference.

``-d``, ``--debug``
   Write debugging information to the logfile. This option produces a
   high volume of output, and would generally only be needed when
   debugging a problem. This option implies the ``--output`` option, as
   well.

``-s``, ``--stack``
   Dump a Python stack trace instead of swallowing exceptions. This
   forces Cedar Backup to dump the entire Python stack trace associated
   with an error, rather than just propagating last message it received
   back up to the user interface. Under some circumstances, this is
   useful information to include along with a bug report.

``-D``, ``--diagnostics``
   Display runtime diagnostic information and then exit. This diagnostic
   information is often useful when filing a bug report.

``-v``, ``--verifyOnly``
   Only verify the S3 bucket contents against the directory on disk. Do
   not make any changes to the S3 bucket or transfer any files. This is
   intended as a quick check to see whether the sync is up-to-date.

   Although no files are transferred, the tool will still execute the
   source filename encoding check, discussed below along with
   ``--ignoreWarnings``.

``-u``, ``--uploadOnly``
   Implement a partial or "upload only" sync, instead of a full synchronization.  
   Normally, synchronization would remove files that exist in S3 but do not exist 
   in the directory on disk.  With this flag, new files are uploaded, but no 
   files are removed in S3.

``-w``, ``--ignoreWarnings``
   The AWS CLI S3 sync process is very picky about filename encoding.
   Files that the Linux filesystem handles with no problems can cause
   problems in S3 if the filename cannot be encoded properly in your
   configured locale. As of this writing, filenames like this will cause
   the sync process to abort without transferring all files as expected.

   To avoid confusion, the ``cback3-amazons3-sync`` tries to guess which
   files in the source directory will cause problems, and refuses to
   execute the AWS CLI S3 sync if any problematic files exist. If you'd
   rather proceed anyway, use ``--ignoreWarnings``.

   If problematic files are found, then you have basically two options:
   either correct your locale (i.e. if you have set ``LANG=C``) or
   rename the file so it can be encoded properly in your locale. The
   error messages will tell you the expected encoding (from your locale)
   and the actual detected encoding for the filename.

.. _cedar-commandline-cbackspan:

The ``cback3-span`` command
---------------------------

.. _cedar-commandline-cbackspan-intro:

Introduction
~~~~~~~~~~~~

Cedar Backup was designed --- and is still primarily focused --- around weekly
backups. Most users who back up more data than fits on a single disc seem to
either use Amazon S3 or stop their backup process at the stage step, using
Cedar Backup as an easy way to collect data.

However, some users have expressed a need to write these large kinds of
backups to disc --- if not every day, then at least occassionally. The
``cback3-span`` tool was written to meet those needs. If you have staged
more data than fits on a single CD or DVD, you can use ``cback3-span``
to split that data between multiple discs.

``cback3-span`` is not a general-purpose disc-splitting tool. It is a
specialized program that requires Cedar Backup configuration to run. All
it can do is read Cedar Backup configuration, find any staging
directories that have not yet been written to disc, and split the files
in those directories between discs.

``cback3-span`` accepts many of the same command-line options as
``cback3``, but *must* be run interactively. It cannot be run from cron.
This is intentional. It is intended to be a useful tool, not a new part
of the backup process (that is the purpose of an extension).

In order to use ``cback3-span``, you must configure your backup such
that the largest individual backup file can fit on a single disc. *The
command will not split a single file onto more than one disc.* All it
can do is split large directories onto multiple discs. Files in those
directories will be arbitrarily split up so that space is utilized most
efficiently.

.. _cedar-commandline-cbackspan-syntax:

Syntax
~~~~~~

The ``cback3-span`` command has the following syntax:

::

    Usage: cback3-span [switches]

    Cedar Backup 'span' tool.

    This Cedar Backup utility spans staged data between multiple discs.
    It is a utility, not an extension, and requires user interaction.

    The following switches are accepted, mostly to set up underlying
    Cedar Backup functionality:

      -h, --help     Display this usage/help listing
      -V, --version  Display version information
      -b, --verbose  Print verbose output as well as logging to disk
      -c, --config   Path to config file (default: /etc/cback3.conf)
      -l, --logfile  Path to logfile (default: /var/log/cback3.log)
      -o, --owner    Logfile ownership, user:group (default: root:adm)
      -m, --mode     Octal logfile permissions mode (default: 640)
      -O, --output   Record some sub-command (i.e. cdrecord) output to the log
      -d, --debug    Write debugging information to the log (implies --output)
      -s, --stack    Dump a Python stack trace instead of swallowing exceptions
            

.. _cedar-commandline-cbackspan-options:

Switches
~~~~~~~~

``-h``, ``--help``
   Display usage/help listing.

``-V``, ``--version``
   Display version information.

``-b``, ``--verbose``
   Print verbose output to the screen as well writing to the logfile.
   When this option is enabled, most information that would normally be
   written to the logfile will also be written to the screen.

``-c``, ``--config``
   Specify the path to an alternate configuration file. The default
   configuration file is ``/etc/cback3.conf``.

``-l``, ``--logfile``
   Specify the path to an alternate logfile. The default logfile file is
   ``/var/log/cback3.log``.

``-o``, ``--owner``
   Specify the ownership of the logfile, in the form ``user:group``. The
   default ownership is ``root:adm``, to match the Debian standard for
   most logfiles. This value will only be used when creating a new
   logfile. If the logfile already exists when the ``cback3`` command is
   executed, it will retain its existing ownership and mode. Only user
   and group names may be used, not numeric uid and gid values.

``-m``, ``--mode``
   Specify the permissions for the logfile, using the numeric mode as in
   ``chmod(1)``. The default mode is ``0640`` (``-rw-r-----``). This value
   will only be used when creating a new logfile. If the logfile already
   exists when the ``cback3`` command is executed, it will retain its
   existing ownership and mode.

``-O``, ``--output``
   Record some sub-command output to the logfile. When this option is
   enabled, all output from system commands will be logged. This might
   be useful for debugging or just for reference. Cedar Backup uses
   system commands mostly for dealing with the CD/DVD recorder and its
   media.

``-d``, ``--debug``
   Write debugging information to the logfile. This option produces a
   high volume of output, and would generally only be needed when
   debugging a problem. This option implies the ``--output`` option, as
   well.

``-s``, ``--stack``
   Dump a Python stack trace instead of swallowing exceptions. This
   forces Cedar Backup to dump the entire Python stack trace associated
   with an error, rather than just propagating last message it received
   back up to the user interface. Under some circumstances, this is
   useful information to include along with a bug report.

.. _cedar-commandline-cbackspan-using:

Using ``cback3-span``
~~~~~~~~~~~~~~~~~~~~~

As discussed above, the ``cback3-span`` is an interactive command. It
cannot be run from cron.

You can typically use the default answer for most questions. The only
two questions that you may not want the default answer for are the fit
algorithm and the cushion percentage.

The cushion percentage is used by ``cback3-span`` to determine what
capacity to shoot for when splitting up your staging directories. A 650
MB disc does not fit fully 650 MB of data. It's usually more like 627 MB
of data. The cushion percentage tells ``cback3-span`` how much overhead
to reserve for the filesystem. The default of 4% is usually OK, but if
you have problems you may need to increase it slightly.

The fit algorithm tells ``cback3-span`` how it should determine which
items should be placed on each disc. If you don't like the result from
one algorithm, you can reject that solution and choose a different
algorithm.

The four available fit algorithms are:

``worst``
   The worst-fit algorithm.

   The worst-fit algorithm proceeds through a sorted list of items
   (sorted from smallest to largest) until running out of items or
   meeting capacity exactly. If capacity is exceeded, the item that
   caused capacity to be exceeded is thrown away and the next one is
   tried. The algorithm effectively includes the maximum number of items
   possible in its search for optimal capacity utilization. It tends to
   be somewhat slower than either the best-fit or alternate-fit
   algorithm, probably because on average it has to look at more items
   before completing.

``best``
   The best-fit algorithm.

   The best-fit algorithm proceeds through a sorted list of items
   (sorted from largest to smallest) until running out of items or
   meeting capacity exactly. If capacity is exceeded, the item that
   caused capacity to be exceeded is thrown away and the next one is
   tried. The algorithm effectively includes the minimum number of items
   possible in its search for optimal capacity utilization. For large
   lists of mixed-size items, it's not unusual to see the algorithm
   achieve 100% capacity utilization by including fewer than 1% of the
   items. Probably because it often has to look at fewer of the items
   before completing, it tends to be a little faster than the worst-fit
   or alternate-fit algorithms.

``first``
   The first-fit algorithm.

   The first-fit algorithm proceeds through an unsorted list of items
   until running out of items or meeting capacity exactly. If capacity
   is exceeded, the item that caused capacity to be exceeded is thrown
   away and the next one is tried. This algorithm generally performs
   more poorly than the other algorithms both in terms of capacity
   utilization and item utilization, but can be as much as an order of
   magnitude faster on large lists of items because it doesn't require
   any sorting.

``alternate``
   A hybrid algorithm that I call alternate-fit.

   This algorithm tries to balance small and large items to achieve
   better end-of-disk performance. Instead of just working one direction
   through a list, it alternately works from the start and end of a
   sorted list (sorted from smallest to largest), throwing away any item
   which causes capacity to be exceeded. The algorithm tends to be
   slower than the best-fit and first-fit algorithms, and slightly
   faster than the worst-fit algorithm, probably because of the number
   of items it considers on average before completing. It often achieves
   slightly better capacity utilization than the worst-fit algorithm,
   while including slightly fewer items.

.. _cedar-commandline-cbackspan-sample:

Sample run
~~~~~~~~~~

Below is a log showing a sample ``cback3-span`` run.

::

   ================================================
              Cedar Backup 'span' tool
   ================================================

   This the Cedar Backup span tool.  It is used to split up staging
   data when that staging data does not fit onto a single disc.

   This utility operates using Cedar Backup configuration.  Configuration
   specifies which staging directory to look at and which writer device
   and media type to use.

   Continue? [Y/n]: 
   ===

   Cedar Backup store configuration looks like this:

      Source Directory...: /tmp/staging
      Media Type.........: cdrw-74
      Device Type........: cdwriter
      Device Path........: /dev/cdrom
      Device SCSI ID.....: None
      Drive Speed........: None
      Check Data Flag....: True
      No Eject Flag......: False

   Is this OK? [Y/n]: 
   ===

   Please wait, indexing the source directory (this may take a while)...
   ===

   The following daily staging directories have not yet been written to disc:

      /tmp/staging/2007/02/07
      /tmp/staging/2007/02/08
      /tmp/staging/2007/02/09
      /tmp/staging/2007/02/10
      /tmp/staging/2007/02/11
      /tmp/staging/2007/02/12
      /tmp/staging/2007/02/13
      /tmp/staging/2007/02/14

   The total size of the data in these directories is 1.00 GB.

   Continue? [Y/n]: 
   ===

   Based on configuration, the capacity of your media is 650.00 MB.

   Since estimates are not perfect and there is some uncertainly in
   media capacity calculations, it is good to have a "cushion",
   a percentage of capacity to set aside.  The cushion reduces the
   capacity of your media, so a 1.5% cushion leaves 98.5% remaining.

   What cushion percentage? [4.00]: 
   ===

   The real capacity, taking into account the 4.00% cushion, is 627.25 MB.
   It will take at least 2 disc(s) to store your 1.00 GB of data.

   Continue? [Y/n]: 
   ===

   Which algorithm do you want to use to span your data across
   multiple discs?

   The following algorithms are available:

      first....: The "first-fit" algorithm
      best.....: The "best-fit" algorithm
      worst....: The "worst-fit" algorithm
      alternate: The "alternate-fit" algorithm

   If you don't like the results you will have a chance to try a
   different one later.

   Which algorithm? [worst]: 
   ===

   Please wait, generating file lists (this may take a while)...
   ===

   Using the "worst-fit" algorithm, Cedar Backup can split your data
   into 2 discs.

   Disc 1: 246 files, 615.97 MB, 98.20% utilization
   Disc 2: 8 files, 412.96 MB, 65.84% utilization

   Accept this solution? [Y/n]: n
   ===

   Which algorithm do you want to use to span your data across
   multiple discs?

   The following algorithms are available:

      first....: The "first-fit" algorithm
      best.....: The "best-fit" algorithm
      worst....: The "worst-fit" algorithm
      alternate: The "alternate-fit" algorithm

   If you don't like the results you will have a chance to try a
   different one later.

   Which algorithm? [worst]: alternate
   ===

   Please wait, generating file lists (this may take a while)...
   ===

   Using the "alternate-fit" algorithm, Cedar Backup can split your data
   into 2 discs.

   Disc 1: 73 files, 627.25 MB, 100.00% utilization
   Disc 2: 181 files, 401.68 MB, 64.04% utilization

   Accept this solution? [Y/n]: y
   ===

   Please place the first disc in your backup device.
   Press return when ready.
   ===

   Initializing image...
   Writing image to disc...

----------

*Previous*: :doc:`install` • *Next*: :doc:`config`

----------

.. [1]
   Some users find this surprising, because extensions are configured
   with sequence numbers. I did it this way because I felt that running
   extensions as part of the all action would sometimes result in
   “surprising” behavior. Better to be definitive than confusing.

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
