.. _cedar-config:

Configuration
=============

.. _cedar-config-overview:

Overview
--------

Configuring Cedar Backup is unfortunately somewhat complicated. The good
news is that once you get through the initial configuration process,
you'll hardly ever have to change anything. Even better, the most
typical changes (i.e. adding and removing directories from a backup) are
easy.

First, familiarize yourself with the concepts in :doc:`basic`.
In particular, be sure that you understand the differences between a
master and a client. (If you only have one machine, then your machine
will act as both a master and a client, and we'll refer to your setup as
a pool of one.) Then, install Cedar Backup per the instructions in
:doc:`install`.

Once everything has been installed, you are ready to begin configuring Cedar
Backup. Look over :doc:`commandline` to become familiar with the command line
interface. Then, look over *Configuration File Format* (below) and create a
configuration file for each peer in your backup pool. To start with, create a
very simple configuration file, then expand it later. Decide now whether you
will store the configuration file in the standard place (``/etc/cback3.conf``)
or in some other location.

After you have all of the configuration files in place, configure each
of your machines, following the instructions in the appropriate section
below (for master, client or pool of one). Since the master and
client(s) must communicate over the network, you won't be able to fully
configure the master without configuring each client and vice-versa. The
instructions are clear on what needs to be done.

Cedar Backup has been designed for use on all UNIX-like systems.
However, since it was developed on a Debian GNU/Linux system, and
because I am a Debian developer, the packaging is prettier and the setup
is somewhat simpler on a Debian system than on a system where you
install from source.

The configuration instructions below have been generalized so they
should work well regardless of what platform you are running (i.e.
RedHat, Gentoo, FreeBSD, etc.). If instructions vary for a particular
platform, you will find a note related to that platform.

I am always open to adding more platform-specific hints and notes, so
write me if you find problems with these instructions.

.. _cedar-config-configfile:

Configuration File Format
-------------------------

Cedar Backup is configured through an XML  [1]_ configuration file,
usually called ``/etc/cback3.conf``. The configuration file contains the
following sections: reference, options, collect, stage, store, purge and
extensions.

All configuration files must contain the two general configuration
sections, the reference section and the options section. Besides that,
administrators need only configure actions they intend to use. For
instance, on a client machine, administrators will generally only
configure the collect and purge sections, while on a master machine they
will have to configure all four action-related sections.  [2]_ The
extensions section is always optional and can be omitted unless
extensions are in use.

   |note|

   Even though the Mac OS X (darwin) filesystem is *not* case-sensitive,
   Cedar Backup configuration *is* generally case-sensitive on that
   platform, just like on all other platforms. For instance, even though
   the files “Ken” and “ken” might be the same on the Mac OS X
   filesystem, an exclusion in Cedar Backup configuration for “ken” will
   only match the file if it is actually on the filesystem with a
   lower-case “k” as its first letter. This won't surprise the typical
   UNIX user, but might surprise someone who's gotten into the “Mac
   Mindset”.

.. _cedar-config-configfile-sample:

Sample Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~

Both the Python source distribution and the Debian package come with a
sample configuration file. The Debian package includes its sample in
``/usr/share/doc/cedar-backup3/examples/cback3.conf.sample``.

This is a sample configuration file similar to the one provided in the
source package. Documentation below provides more information about each
of the individual configuration sections.

::

   <?xml version="1.0"?>
   <cb_config>
      <reference>
         <author>Kenneth J. Pronovici</author>
         <revision>1.3</revision>
         <description>Sample</description>
      </reference>
      <options>
         <starting_day>tuesday</starting_day>
         <working_dir>/opt/backup/tmp</working_dir>
         <backup_user>backup</backup_user>
         <backup_group>group</backup_group>
         <rcp_command>/usr/bin/scp -B</rcp_command>
      </options>
      <peers>
         <peer>
            <name>debian</name>
            <type>local</type>
            <collect_dir>/opt/backup/collect</collect_dir>
         </peer>
      </peers>
      <collect>
         <collect_dir>/opt/backup/collect</collect_dir>
         <collect_mode>daily</collect_mode>
         <archive_mode>targz</archive_mode>
         <ignore_file>.cbignore</ignore_file>
         <dir>
            <abs_path>/etc</abs_path>
            <collect_mode>incr</collect_mode>
         </dir>
         <file>
            <abs_path>/home/root/.profile</abs_path>
            <collect_mode>weekly</collect_mode>
         </file>
      </collect>
      <stage>
         <staging_dir>/opt/backup/staging</staging_dir>
      </stage>
      <store>
         <source_dir>/opt/backup/staging</source_dir>
         <media_type>cdrw-74</media_type>
         <device_type>cdwriter</device_type>
         <target_device>/dev/cdrw</target_device>
         <target_scsi_id>0,0,0</target_scsi_id>
         <drive_speed>4</drive_speed>
         <check_data>Y</check_data>
         <check_media>Y</check_media>
         <warn_midnite>Y</warn_midnite>
      </store>
      <purge>
         <dir>
            <abs_path>/opt/backup/stage</abs_path>
            <retain_days>7</retain_days>
         </dir>
         <dir>
            <abs_path>/opt/backup/collect</abs_path>
            <retain_days>0</retain_days>
         </dir>
      </purge>
   </cb_config>
            

.. _cedar-config-configfile-reference:

Reference Configuration
~~~~~~~~~~~~~~~~~~~~~~~

The reference configuration section contains free-text elements that
exist only for reference.. The section itself is required, but the
individual elements may be left blank if desired.

This is an example reference configuration section:

::

   <reference>
      <author>Kenneth J. Pronovici</author>
      <revision>Revision 1.3</revision>
      <description>Sample</description>
      <generator>Yet to be Written Config Tool (tm)</description>
   </reference>
            

The following elements are part of the reference configuration section:

``author``
   Author of the configuration file.

   *Restrictions:* None

``revision``
   Revision of the configuration file.

   *Restrictions:* None

``description``
   Description of the configuration file.

   *Restrictions:* None

``generator``
   Tool that generated the configuration file, if any.

   *Restrictions:* None

.. _cedar-config-configfile-options:

Options Configuration
~~~~~~~~~~~~~~~~~~~~~

The options configuration section contains configuration options that
are not specific to any one action.

This is an example options configuration section:

::

   <options>
      <starting_day>tuesday</starting_day>
      <working_dir>/opt/backup/tmp</working_dir>
      <backup_user>backup</backup_user>
      <backup_group>backup</backup_group>
      <rcp_command>/usr/bin/scp -B</rcp_command>
      <rsh_command>/usr/bin/ssh</rsh_command>
      <cback_command>/usr/bin/cback</cback_command>
      <managed_actions>collect, purge</managed_actions>
      <override>
         <command>cdrecord</command>
         <abs_path>/opt/local/bin/cdrecord</abs_path>
      </override>
      <override>
         <command>mkisofs</command>
         <abs_path>/opt/local/bin/mkisofs</abs_path>
      </override>
      <pre_action_hook>
         <action>collect</action>
         <command>echo "I AM A PRE-ACTION HOOK RELATED TO COLLECT"</command>
      </pre_action_hook>
      <post_action_hook>
         <action>collect</action>
         <command>echo "I AM A POST-ACTION HOOK RELATED TO COLLECT"</command>
      </post_action_hook>
   </options>
            

The following elements are part of the options configuration section:

``starting_day``
   Day that starts the week.

   Cedar Backup is built around the idea of weekly backups. The starting
   day of week is the day that media will be rebuilt from scratch and
   that incremental backup information will be cleared.

   *Restrictions:* Must be a day of the week in English, i.e.
   ``monday``, ``tuesday``, etc. The validation is case-sensitive.

``working_dir``
   Working (temporary) directory to use for backups.

   This directory is used for writing temporary files, such as tar file
   or ISO filesystem images as they are being built. It is also used to
   store day-to-day information about incremental backups.

   The working directory should contain enough free space to hold
   temporary tar files (on a client) or to build an ISO filesystem image
   (on a master).

   *Restrictions:* Must be an absolute path

``backup_user``
   Effective user that backups should run as.

   This user must exist on the machine which is being configured and
   should not be root (although that restriction is not enforced).

   This value is also used as the default remote backup user for remote
   peers.

   *Restrictions:* Must be non-empty

``backup_group``
   Effective group that backups should run as.

   This group must exist on the machine which is being configured, and
   should not be root or some other “powerful” group (although that
   restriction is not enforced).

   *Restrictions:* Must be non-empty

``rcp_command``
   Default rcp-compatible copy command for staging.

   The rcp command should be the exact command used for remote copies,
   including any required options. If you are using ``scp``, you should
   pass it the ``-B`` option, so ``scp`` will not ask for any user input
   (which could hang the backup). A common example is something like
   ``/usr/bin/scp -B``.

   This value is used as the default value for all remote peers.
   Technically, this value is not needed by clients, but we require it
   for all config files anyway.

   *Restrictions:* Must be non-empty

``rsh_command``
   Default rsh-compatible command to use for remote shells.

   The rsh command should be the exact command used for remote shells,
   including any required options.

   This value is used as the default value for all managed clients. It
   is optional, because it is only used when executing actions on
   managed clients. However, each managed client must either be able to
   read the value from options configuration or must set the value
   explicitly.

   *Restrictions:* Must be non-empty

``cback_command``
   Default cback-compatible command to use on managed remote clients.

   The cback command should be the exact command used for for executing
   ``cback`` on a remote managed client, including any required
   command-line options. Do *not* list any actions in the command line,
   and do *not* include the ``--full`` command-line option.

   This value is used as the default value for all managed clients. It
   is optional, because it is only used when executing actions on
   managed clients. However, each managed client must either be able to
   read the value from options configuration or must set the value
   explicitly.

   *Note:* if this command-line is complicated, it is often better to
   create a simple shell script on the remote host to encapsulate all of
   the options. Then, just reference the shell script in configuration.

   *Restrictions:* Must be non-empty

``managed_actions``
   Default set of actions that are managed on remote clients.

   This is a comma-separated list of actions that the master will manage
   on behalf of remote clients. Typically, it would include only
   collect-like actions and purge.

   This value is used as the default value for all managed clients. It
   is optional, because it is only used when executing actions on
   managed clients. However, each managed client must either be able to
   read the value from options configuration or must set the value
   explicitly.

   *Restrictions:* Must be non-empty.

``override``
   Command to override with a customized path.

   This is a subsection which contains a command to override with a
   customized path. This functionality would be used if root's ``$PATH``
   does not include a particular required command, or if there is a need
   to use a version of a command that is different than the one listed
   on the ``$PATH``. Most users will only use this section when directed
   to, in order to fix a problem.

   This section is optional, and can be repeated as many times as
   necessary.

   This subsection must contain the following two fields:

   ``command``
      Name of the command to be overridden, i.e. “cdrecord”.

      *Restrictions:* Must be a non-empty string.

   ``abs_path``
      The absolute path where the overridden command can be found.

      *Restrictions:* Must be an absolute path.

``pre_action_hook``
   Hook configuring a command to be executed before an action.

   This is a subsection which configures a command to be executed
   immediately before a named action. It provides a way for
   administrators to associate their own custom functionality with
   standard Cedar Backup actions or with arbitrary extensions.

   This section is optional, and can be repeated as many times as
   necessary.

   This subsection must contain the following two fields:

   ``action``
      Name of the Cedar Backup action that the hook is associated with.
      The action can be a standard backup action (collect, stage, etc.)
      or can be an extension action. No validation is done to ensure
      that the configured action actually exists.

      *Restrictions:* Must be a non-empty string.

   ``command``
      Name of the command to be executed. This item can either specify
      the path to a shell script of some sort (the recommended approach)
      or can include a complete shell command.

      *Note:* if you choose to provide a complete shell command rather
      than the path to a script, you need to be aware of some
      limitations of Cedar Backup's command-line parser. You cannot use
      a subshell (via the :literal:`\`command\`` or ``$(command)``
      syntaxes) or any shell variable in your command line.
      Additionally, the command-line parser only recognizes the
      double-quote character (``"``) to delimit groupings or strings on
      the command-line. The bottom line is, you are probably best off
      writing a shell script of some sort for anything more
      sophisticated than very simple shell commands.

      *Restrictions:* Must be a non-empty string.

``post_action_hook``
   Hook configuring a command to be executed after an action.

   This is a subsection which configures a command to be executed
   immediately after a named action. It provides a way for
   administrators to associate their own custom functionality with
   standard Cedar Backup actions or with arbitrary extensions.

   This section is optional, and can be repeated as many times as
   necessary.

   This subsection must contain the following two fields:

   ``action``
      Name of the Cedar Backup action that the hook is associated with.
      The action can be a standard backup action (collect, stage, etc.)
      or can be an extension action. No validation is done to ensure
      that the configured action actually exists.

      *Restrictions:* Must be a non-empty string.

   ``command``
      Name of the command to be executed. This item can either specify
      the path to a shell script of some sort (the recommended approach)
      or can include a complete shell command.

      *Note:* if you choose to provide a complete shell command rather
      than the path to a script, you need to be aware of some
      limitations of Cedar Backup's command-line parser. You cannot use
      a subshell (via the :literal:`\`command\`` or ``$(command)``
      syntaxes) or any shell variable in your command line.
      Additionally, the command-line parser only recognizes the
      double-quote character (``"``) to delimit groupings or strings on
      the command-line. The bottom line is, you are probably best off
      writing a shell script of some sort for anything more
      sophisticated than very simple shell commands.

      *Restrictions:* Must be a non-empty string.

.. _cedar-config-configfile-peers:

Peers Configuration
~~~~~~~~~~~~~~~~~~~

The peers configuration section contains a list of the peers managed by
a master. This section is only required on a master.

This is an example peers configuration section:

::

   <peers>
      <peer>
         <name>machine1</name>
         <type>local</type>
         <collect_dir>/opt/backup/collect</collect_dir>
      </peer>
      <peer>
         <name>machine2</name>
         <type>remote</type>
         <backup_user>backup</backup_user>
         <collect_dir>/opt/backup/collect</collect_dir>
         <ignore_failures>all</ignore_failures>
      </peer>
      <peer>
         <name>machine3</name>
         <type>remote</type>
         <managed>Y</managed>
         <backup_user>backup</backup_user>
         <collect_dir>/opt/backup/collect</collect_dir>
         <rcp_command>/usr/bin/scp</rcp_command>
         <rsh_command>/usr/bin/ssh</rsh_command>
         <cback_command>/usr/bin/cback</cback_command>
         <managed_actions>collect, purge</managed_actions>
      </peer>
   </peers>
            

The following elements are part of the peers configuration section:

``peer`` (local version)
   Local client peer in a backup pool.

   This is a subsection which contains information about a specific
   local client peer managed by a master.

   This section can be repeated as many times as is necessary. At least
   one remote or local peer must be configured.

   The local peer subsection must contain the following fields:

   ``name``
      Name of the peer, typically a valid hostname.

      For local peers, this value is only used for reference. However,
      it is good practice to list the peer's hostname here, for
      consistency with remote peers.

      *Restrictions:* Must be non-empty, and unique among all peers.

   ``type``
      Type of this peer.

      This value identifies the type of the peer. For a local peer, it
      must always be ``local``.

      *Restrictions:* Must be ``local``.

   ``collect_dir``
      Collect directory to stage from for this peer.

      The master will copy all files in this directory into the
      appropriate staging directory. Since this is a local peer, the
      directory is assumed to be reachable via normal filesystem
      operations (i.e. ``cp``).

      *Restrictions:* Must be an absolute path.

   ``ignore_failures``
      Ignore failure mode for this peer

      The ignore failure mode indicates whether “not ready to be staged”
      errors should be ignored for this peer. This option is intended to
      be used for peers that are up only intermittently, to cut down on
      the number of error emails received by the Cedar Backup
      administrator.

      The "none" mode means that all errors will be reported. This is
      the default behavior. The "all" mode means to ignore all failures.
      The "weekly" mode means to ignore failures for a start-of-week or
      full backup. The "daily" mode means to ignore failures for any
      backup that is not either a full backup or a start-of-week backup.

      *Restrictions:* If set, must be one of "none", "all", "daily", or
      "weekly".

``peer`` (remote version)
   Remote client peer in a backup pool.

   This is a subsection which contains information about a specific
   remote client peer managed by a master. A remote peer is one which
   can be reached via an rsh-based network call.

   This section can be repeated as many times as is necessary. At least
   one remote or local peer must be configured.

   The remote peer subsection must contain the following fields:

   ``name``
      Hostname of the peer.

      For remote peers, this must be a valid DNS hostname or IP address
      which can be resolved during an rsh-based network call.

      *Restrictions:* Must be non-empty, and unique among all peers.

   ``type``
      Type of this peer.

      This value identifies the type of the peer. For a remote peer, it
      must always be ``remote``.

      *Restrictions:* Must be ``remote``.

   ``managed``
      Indicates whether this peer is managed.

      A managed peer (or managed client) is a peer for which the master
      manages all of the backup activites via a remote shell.

      This field is optional. If it doesn't exist, then ``N`` will be
      assumed.

      *Restrictions:* Must be a boolean (``Y`` or ``N``).

   ``collect_dir``
      Collect directory to stage from for this peer.

      The master will copy all files in this directory into the
      appropriate staging directory. Since this is a remote peer, the
      directory is assumed to be reachable via rsh-based network
      operations (i.e. ``scp`` or the configured rcp command).

      *Restrictions:* Must be an absolute path.

   ``ignore_failures``
      Ignore failure mode for this peer

      The ignore failure mode indicates whether “not ready to be staged”
      errors should be ignored for this peer. This option is intended to
      be used for peers that are up only intermittently, to cut down on
      the number of error emails received by the Cedar Backup
      administrator.

      The "none" mode means that all errors will be reported. This is
      the default behavior. The "all" mode means to ignore all failures.
      The "weekly" mode means to ignore failures for a start-of-week or
      full backup. The "daily" mode means to ignore failures for any
      backup that is not either a full backup or a start-of-week backup.

      *Restrictions:* If set, must be one of "none", "all", "daily", or
      "weekly".

   ``backup_user``
      Name of backup user on the remote peer.

      This username will be used when copying files from the remote peer
      via an rsh-based network connection.

      This field is optional. if it doesn't exist, the backup will use
      the default backup user from the options section.

      *Restrictions:* Must be non-empty.

   ``rcp_command``
      The rcp-compatible copy command for this peer.

      The rcp command should be the exact command used for remote
      copies, including any required options. If you are using ``scp``,
      you should pass it the ``-B`` option, so ``scp`` will not ask for
      any user input (which could hang the backup). A common example is
      something like ``/usr/bin/scp -B``.

      This field is optional. if it doesn't exist, the backup will use
      the default rcp command from the options section.

      *Restrictions:* Must be non-empty.

   ``rsh_command``
      The rsh-compatible command for this peer.

      The rsh command should be the exact command used for remote
      shells, including any required options.

      This value only applies if the peer is managed.

      This field is optional. if it doesn't exist, the backup will use
      the default rsh command from the options section.

      *Restrictions:* Must be non-empty

   ``cback_command``
      The cback-compatible command for this peer.

      The cback command should be the exact command used for for
      executing cback on the peer as part of a managed backup. This
      value must include any required command-line options. Do *not*
      list any actions in the command line, and do *not* include the
      ``--full`` command-line option.

      This value only applies if the peer is managed.

      This field is optional. if it doesn't exist, the backup will use
      the default cback command from the options section.

      *Note:* if this command-line is complicated, it is often better to
      create a simple shell script on the remote host to encapsulate all
      of the options. Then, just reference the shell script in
      configuration.

      *Restrictions:* Must be non-empty

   ``managed_actions``
      Set of actions that are managed for this peer.

      This is a comma-separated list of actions that the master will
      manage on behalf this peer. Typically, it would include only
      collect-like actions and purge.

      This value only applies if the peer is managed.

      This field is optional. if it doesn't exist, the backup will use
      the default list of managed actions from the options section.

      *Restrictions:* Must be non-empty.

.. _cedar-config-configfile-collect:

Collect Configuration
~~~~~~~~~~~~~~~~~~~~~

The collect configuration section contains configuration options related
the the collect action. This section contains a variable number of
elements, including an optional exclusion section and a repeating
subsection used to specify which directories and/or files to collect.
You can also configure an ignore indicator file, which lets users mark
their own directories as not backed up.

Sometimes, it's not very convenient to list directories one by one in
the Cedar Backup configuration file. For instance, when backing up your
home directory, you often exclude as many directories as you include.
The ignore file mechanism can be of some help, but it still isn't very
convenient if there are a lot of directories to ignore (or if new
directories pop up all of the time).

In this situation, one option is to use a link farm rather than listing
all of the directories in configuration. A link farm is a directory that
contains nothing but a set of soft links to other files and directories.
Normally, Cedar Backup does not follow soft links, but you can override
this behavior for individual directories using the ``link_depth`` and
``dereference`` options (see below).

When using a link farm, you still have to deal with each backed-up
directory individually, but you don't have to modify configuration. Some
users find that this works better for them.

In order to actually execute the collect action, you must have
configured at least one collect directory or one collect file. However,
if you are only including collect configuration for use by an extension,
then it's OK to leave out these sections. The validation will take place
only when the collect action is executed.

This is an example collect configuration section:

::

   <collect>
      <collect_dir>/opt/backup/collect</collect_dir>
      <collect_mode>daily</collect_mode>
      <archive_mode>targz</archive_mode>
      <ignore_file>.cbignore</ignore_file>
      <exclude>
         <abs_path>/etc</abs_path>
         <pattern>.*\.conf</pattern>
      </exclude>
      <file>
         <abs_path>/home/root/.profile</abs_path>
      </file>
      <dir>
         <abs_path>/etc</abs_path>
      </dir>
      <dir>
         <abs_path>/var/log</abs_path>
         <collect_mode>incr</collect_mode>
      </dir>
      <dir>
         <abs_path>/opt</abs_path>
         <collect_mode>weekly</collect_mode>
         <exclude>
            <abs_path>/opt/large</abs_path>
            <rel_path>backup</rel_path>
            <pattern>.*tmp</pattern>
         </exclude>
      </dir>
   </collect>
            

The following elements are part of the collect configuration section:

``collect_dir``
   Directory to collect files into.

   On a client, this is the directory which tarfiles for individual
   collect directories are written into. The master then stages files
   from this directory into its own staging directory.

   This field is always required. It must contain enough free space to
   collect all of the backed-up files on the machine in a compressed
   form.

   *Restrictions:* Must be an absolute path

``collect_mode``
   Default collect mode.

   The collect mode describes how frequently a directory is backed up.
   See :doc:`basic` for more information.

   This value is the collect mode that will be used by default during
   the collect process. Individual collect directories (below) may
   override this value. If *all* individual directories provide their
   own value, then this default value may be omitted from configuration.

   *Note:* if your backup device does not suppport multisession discs,
   then you should probably use the ``daily`` collect mode to avoid
   losing data.

   *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

``archive_mode``
   Default archive mode for collect files.

   The archive mode maps to the way that a backup file is stored. A
   value ``tar`` means just a tarfile (``file.tar``); a value ``targz``
   means a gzipped tarfile (``file.tar.gz``); and a value ``tarbz2``
   means a bzipped tarfile (``file.tar.bz2``)

   This value is the archive mode that will be used by default during
   the collect process. Individual collect directories (below) may
   override this value. If *all* individual directories provide their
   own value, then this default value may be omitted from configuration.

   *Restrictions:* Must be one of ``tar``, ``targz`` or ``tarbz2``.

``ignore_file``
   Default ignore file name.

   The ignore file is an indicator file. If it exists in a given
   directory, then that directory will be recursively excluded from the
   backup as if it were explicitly excluded in configuration.

   The ignore file provides a way for individual users (who might not
   have access to Cedar Backup configuration) to control which of their
   own directories get backed up. For instance, users with a ``~/tmp``
   directory might not want it backed up. If they create an ignore file
   in their directory (e.g. ``~/tmp/.cbignore``), then Cedar Backup will
   ignore it.

   This value is the ignore file name that will be used by default
   during the collect process. Individual collect directories (below)
   may override this value. If *all* individual directories provide
   their own value, then this default value may be omitted from
   configuration.

   *Restrictions:* Must be non-empty

``recursion_level``
   Recursion level to use when collecting directories.

   This is an integer value that Cedar Backup will consider when
   generating archive files for a configured collect directory.

   Normally, Cedar Backup generates one archive file per collect
   directory. So, if you collect ``/etc`` you get ``etc.tar.gz``. Most
   of the time, this is what you want. However, you may sometimes wish
   to generate multiple archive files for a single collect directory.

   The most obvious example is for ``/home``. By default, Cedar Backup
   will generate ``home.tar.gz``. If instead, you want one archive file
   per home directory you can set a recursion level of ``1``. Cedar
   Backup will generate ``home-user1.tar.gz``, ``home-user2.tar.gz``,
   etc.

   Higher recursion levels (``2``, ``3``, etc.) are legal, and it
   doesn't matter if the configured recursion level is deeper than the
   directory tree that is being collected. You can use a negative
   recursion level (like ``-1``) to specify an infinite level of
   recursion. This will exhaust the tree in the same way as if the
   recursion level is set too high.

   This field is optional. if it doesn't exist, the backup will use the
   default recursion level of zero.

   *Restrictions:* Must be an integer.

``exclude``
   List of paths or patterns to exclude from the backup.

   This is a subsection which contains a set of absolute paths and
   patterns to be excluded across all configured directories. For a
   given directory, the set of absolute paths and patterns to exclude is
   built from this list and any list that exists on the directory
   itself. Directories *cannot* override or remove entries that are in
   this list, however.

   This section is optional, and if it exists can also be empty.

   The exclude subsection can contain one or more of each of the
   following fields:

   ``abs_path``
      An absolute path to be recursively excluded from the backup.

      If a directory is excluded, then all of its children are also
      recursively excluded. For instance, a value ``/var/log/apache``
      would exclude any files within ``/var/log/apache`` as well as
      files within other directories under ``/var/log/apache``.

      This field can be repeated as many times as is necessary.

      *Restrictions:* Must be an absolute path.

   ``pattern``
      A pattern to be recursively excluded from the backup.

      The pattern must be a Python regular expression.  [3]_ It is
      assumed to be bounded at front and back by the beginning and end
      of the string (i.e. it is treated as if it begins with ``^`` and
      ends with ``$``).

      If the pattern causes a directory to be excluded, then all of the
      children of that directory are also recursively excluded. For
      instance, a value ``.*apache.*`` might match the
      ``/var/log/apache`` directory. This would exclude any files within
      ``/var/log/apache`` as well as files within other directories
      under ``/var/log/apache``.

      This field can be repeated as many times as is necessary.

      *Restrictions:* Must be non-empty

``file``
   A file to be collected.

   This is a subsection which contains information about a specific file
   to be collected (backed up).

   This section can be repeated as many times as is necessary. At least
   one collect directory or collect file must be configured when the
   collect action is executed.

   The collect file subsection contains the following fields:

   ``abs_path``
      Absolute path of the file to collect.

      *Restrictions:* Must be an absolute path.

   ``collect_mode``
      Collect mode for this file

      The collect mode describes how frequently a file is backed up. See
      :doc:`basic` for more information.

      This field is optional. If it doesn't exist, the backup will use
      the default collect mode.

      *Note:* if your backup device does not suppport multisession discs,
      then you should probably confine yourself to the ``daily`` collect
      mode, to avoid losing data.

      *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

   ``archive_mode``
      Archive mode for this file.

      The archive mode maps to the way that a backup file is stored. A
      value ``tar`` means just a tarfile (``file.tar``); a value
      ``targz`` means a gzipped tarfile (``file.tar.gz``); and a value
      ``tarbz2`` means a bzipped tarfile (``file.tar.bz2``)

      This field is optional. if it doesn't exist, the backup will use
      the default archive mode.

      *Restrictions:* Must be one of ``tar``, ``targz`` or ``tarbz2``.

``dir``
   A directory to be collected.

   This is a subsection which contains information about a specific
   directory to be collected (backed up).

   This section can be repeated as many times as is necessary. At least
   one collect directory or collect file must be configured when the
   collect action is executed.

   The collect directory subsection contains the following fields:

   ``abs_path``
      Absolute path of the directory to collect.

      The path may be either a directory, a soft link to a directory, or
      a hard link to a directory. All three are treated the same at this
      level.

      The contents of the directory will be recursively collected. The
      backup will contain all of the files in the directory, as well as
      the contents of all of the subdirectories within the directory,
      etc.

      Soft links *within* the directory are treated as files, i.e. they
      are copied verbatim (as a link) and their contents are not backed
      up.

      *Restrictions:* Must be an absolute path.

   ``collect_mode``
      Collect mode for this directory

      The collect mode describes how frequently a directory is backed
      up. See :doc:`basic` for more information.

      This field is optional. If it doesn't exist, the backup will use
      the default collect mode.

      *Note:* if your backup device does not suppport multisession discs,
      then you should probably confine yourself to the ``daily`` collect
      mode, to avoid losing data.

      *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

   ``archive_mode``
      Archive mode for this directory.

      The archive mode maps to the way that a backup file is stored. A
      value ``tar`` means just a tarfile (``file.tar``); a value
      ``targz`` means a gzipped tarfile (``file.tar.gz``); and a value
      ``tarbz2`` means a bzipped tarfile (``file.tar.bz2``)

      This field is optional. if it doesn't exist, the backup will use
      the default archive mode.

      *Restrictions:* Must be one of ``tar``, ``targz`` or ``tarbz2``.

   ``ignore_file``
      Ignore file name for this directory.

      The ignore file is an indicator file. If it exists in a given
      directory, then that directory will be recursively excluded from
      the backup as if it were explicitly excluded in configuration.

      The ignore file provides a way for individual users (who might not
      have access to Cedar Backup configuration) to control which of
      their own directories get backed up. For instance, users with a
      ``~/tmp`` directory might not want it backed up. If they create an
      ignore file in their directory (e.g. ``~/tmp/.cbignore``), then
      Cedar Backup will ignore it.

      This field is optional. If it doesn't exist, the backup will use
      the default ignore file name.

      *Restrictions:* Must be non-empty

   ``link_depth``
      Link depth value to use for this directory.

      The link depth is maximum depth of the tree at which soft links
      should be followed. So, a depth of 0 does not follow any soft
      links within the collect directory, a depth of 1 follows only
      links immediately within the collect directory, a depth of 2
      follows the links at the next level down, etc.

      This field is optional. If it doesn't exist, the backup will
      assume a value of zero, meaning that soft links within the collect
      directory will never be followed.

      *Restrictions:* If set, must be an integer GE 0.

   ``dereference``
      Whether to dereference soft links.

      If this flag is set, links that are being followed will be
      dereferenced before being added to the backup. The link will be
      added (as a link), and then the directory or file that the link
      points at will be added as well.

      This value only applies to a directory where soft links are being
      followed (per the ``link_depth`` configuration option). It never
      applies to a configured collect directory itself, only to other
      directories within the collect directory.

      This field is optional. If it doesn't exist, the backup will
      assume that links should never be dereferenced.

      *Restrictions:* Must be a boolean (``Y`` or ``N``).

   ``exclude``
      List of paths or patterns to exclude from the backup.

      This is a subsection which contains a set of paths and patterns to
      be excluded within this collect directory. This list is combined
      with the program-wide list to build a complete list for the
      directory.

      This section is entirely optional, and if it exists can also be
      empty.

      The exclude subsection can contain one or more of each of the
      following fields:

      ``abs_path``
         An absolute path to be recursively excluded from the backup.

         If a directory is excluded, then all of its children are also
         recursively excluded. For instance, a value ``/var/log/apache``
         would exclude any files within ``/var/log/apache`` as well as
         files within other directories under ``/var/log/apache``.

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be an absolute path.

      ``rel_path``
         A relative path to be recursively excluded from the backup.

         The path is assumed to be relative to the collect directory
         itself. For instance, if the configured directory is
         ``/opt/web`` a configured relative path of ``something/else``
         would exclude the path ``/opt/web/something/else``.

         If a directory is excluded, then all of its children are also
         recursively excluded. For instance, a value ``something/else``
         would exclude any files within ``something/else`` as well as
         files within other directories under ``something/else``.

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be non-empty.

      ``pattern``
         A pattern to be excluded from the backup.

         The pattern must be a Python regular expression. It is assumed
         to be bounded at front and back by the beginning and end of the
         string (i.e. it is treated as if it begins with ``^`` and ends
         with ``$``).

         If the pattern causes a directory to be excluded, then all of
         the children of that directory are also recursively excluded.
         For instance, a value ``.*apache.*`` might match the
         ``/var/log/apache`` directory. This would exclude any files
         within ``/var/log/apache`` as well as files within other
         directories under ``/var/log/apache``.

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be non-empty

.. _cedar-config-configfile-stage:

Stage Configuration
~~~~~~~~~~~~~~~~~~~

The stage configuration section contains configuration options related
the the stage action. The section indicates where date from peers can be
staged to.

This section can also (optionally) override the list of peers so that
not all peers are staged. If you provide *any* peers in this section,
then the list of peers here completely replaces the list of peers in the
peers configuration section for the purposes of staging.

This is an example stage configuration section for the simple case where
the list of peers is taken from peers configuration:

::

   <stage>
      <staging_dir>/opt/backup/stage</staging_dir>
   </stage>
            

This is an example stage configuration section that overrides the
default list of peers:

::

   <stage>
      <staging_dir>/opt/backup/stage</staging_dir>
      <peer>
         <name>machine1</name>
         <type>local</type>
         <collect_dir>/opt/backup/collect</collect_dir>
      </peer>
      <peer>
         <name>machine2</name>
         <type>remote</type>
         <backup_user>backup</backup_user>
         <collect_dir>/opt/backup/collect</collect_dir>
      </peer>
   </stage>
            

The following elements are part of the stage configuration section:

``staging_dir``
   Directory to stage files into.

   This is the directory into which the master stages collected data
   from each of the clients. Within the staging directory, data is
   staged into date-based directories by peer name. For instance, peer
   “daystrom” backed up on 19 Feb 2005 would be staged into something
   like ``2005/02/19/daystrom`` relative to the staging directory
   itself.

   This field is always required. The directory must contain enough free
   space to stage all of the files collected from all of the various
   machines in a backup pool. Many administrators set up purging to keep
   staging directories around for a week or more, which requires even
   more space.

   *Restrictions:* Must be an absolute path

``peer`` (local version)
   Local client peer in a backup pool.

   This is a subsection which contains information about a specific
   local client peer to be staged (backed up). A local peer is one whose
   collect directory can be reached without requiring any rsh-based
   network calls. It is possible that a remote peer might be staged as a
   local peer if its collect directory is mounted to the master via NFS,
   AFS or some other method.

   This section can be repeated as many times as is necessary. At least
   one remote or local peer must be configured.

   *Remember*, if you provide *any* local or remote peer in staging
   configuration, the global peer configuration is completely replaced
   by the staging peer configuration.

   The local peer subsection must contain the following fields:

   ``name``
      Name of the peer, typically a valid hostname.

      For local peers, this value is only used for reference. However,
      it is good practice to list the peer's hostname here, for
      consistency with remote peers.

      *Restrictions:* Must be non-empty, and unique among all peers.

   ``type``
      Type of this peer.

      This value identifies the type of the peer. For a local peer, it
      must always be ``local``.

      *Restrictions:* Must be ``local``.

   ``collect_dir``
      Collect directory to stage from for this peer.

      The master will copy all files in this directory into the
      appropriate staging directory. Since this is a local peer, the
      directory is assumed to be reachable via normal filesystem
      operations (i.e. ``cp``).

      *Restrictions:* Must be an absolute path.

``peer`` (remote version)
   Remote client peer in a backup pool.

   This is a subsection which contains information about a specific
   remote client peer to be staged (backed up). A remote peer is one
   whose collect directory can only be reached via an rsh-based network
   call.

   This section can be repeated as many times as is necessary. At least
   one remote or local peer must be configured.

   *Remember*, if you provide *any* local or remote peer in staging
   configuration, the global peer configuration is completely replaced
   by the staging peer configuration.

   The remote peer subsection must contain the following fields:

   ``name``
      Hostname of the peer.

      For remote peers, this must be a valid DNS hostname or IP address
      which can be resolved during an rsh-based network call.

      *Restrictions:* Must be non-empty, and unique among all peers.

   ``type``
      Type of this peer.

      This value identifies the type of the peer. For a remote peer, it
      must always be ``remote``.

      *Restrictions:* Must be ``remote``.

   ``collect_dir``
      Collect directory to stage from for this peer.

      The master will copy all files in this directory into the
      appropriate staging directory. Since this is a remote peer, the
      directory is assumed to be reachable via rsh-based network
      operations (i.e. ``scp`` or the configured rcp command).

      *Restrictions:* Must be an absolute path.

   ``backup_user``
      Name of backup user on the remote peer.

      This username will be used when copying files from the remote peer
      via an rsh-based network connection.

      This field is optional. if it doesn't exist, the backup will use
      the default backup user from the options section.

      *Restrictions:* Must be non-empty.

   ``rcp_command``
      The rcp-compatible copy command for this peer.

      The rcp command should be the exact command used for remote
      copies, including any required options. If you are using ``scp``,
      you should pass it the ``-B`` option, so ``scp`` will not ask for
      any user input (which could hang the backup). A common example is
      something like ``/usr/bin/scp -B``.

      This field is optional. if it doesn't exist, the backup will use
      the default rcp command from the options section.

      *Restrictions:* Must be non-empty.

.. _cedar-config-configfile-store:

Store Configuration
~~~~~~~~~~~~~~~~~~~

The store configuration section contains configuration options related
the the store action. This section contains several optional fields.
Most fields control the way media is written using the writer device.

This is an example store configuration section:

::

   <store>
      <source_dir>/opt/backup/stage</source_dir>
      <media_type>cdrw-74</media_type>
      <device_type>cdwriter</device_type>
      <target_device>/dev/cdrw</target_device>
      <target_scsi_id>0,0,0</target_scsi_id>
      <drive_speed>4</drive_speed>
      <check_data>Y</check_data>
      <check_media>Y</check_media>
      <warn_midnite>Y</warn_midnite>
      <no_eject>N</no_eject>
      <refresh_media_delay>15</refresh_media_delay>
      <eject_delay>2</eject_delay>
      <blank_behavior>
         <mode>weekly</mode>
         <factor>1.3</factor>
      </blank_behavior>
   </store>
            

The following elements are part of the store configuration section:

``source_dir``
   Directory whose contents should be written to media.

   This directory *must* be a Cedar Backup staging directory, as
   configured in the staging configuration section. Only certain data
   from that directory (typically, data from the current day) will be
   written to disc.

   *Restrictions:* Must be an absolute path

``device_type``
   Type of the device used to write the media.

   This field controls which type of writer device will be used by Cedar
   Backup. Currently, Cedar Backup supports CD writers (``cdwriter``)
   and DVD writers (``dvdwriter``).

   This field is optional. If it doesn't exist, the ``cdwriter`` device
   type is assumed.

   *Restrictions:* If set, must be either ``cdwriter`` or ``dvdwriter``.

``media_type``
   Type of the media in the device.

   Unless you want to throw away a backup disc every week, you are
   probably best off using rewritable media.

   You must choose a media type that is appropriate for the device type
   you chose above. For more information on media types, see
   :doc:`basic`.

   *Restrictions:* Must be one of ``cdr-74``, ``cdrw-74``, ``cdr-80`` or
   ``cdrw-80`` if device type is ``cdwriter``; or one of ``dvd+r`` or
   ``dvd+rw`` if device type is ``dvdwriter``.

``target_device``
   Filesystem device name for writer device.

   This value is required for both CD writers and DVD writers.

   This is the UNIX device name for the writer drive, for instance
   ``/dev/scd0`` or a symlink like ``/dev/cdrw``.

   In some cases, this device name is used to directly write to media.
   This is true all of the time for DVD writers, and is true for CD
   writers when a SCSI id (see below) has not been specified.

   Besides this, the device name is also needed in order to do several
   pre-write checks (such as whether the device might already be
   mounted) as well as the post-write consistency check, if enabled.

   *Note:* some users have reported intermittent problems when using a
   symlink as the target device on Linux, especially with DVD media. If
   you experience problems, try using the real device name rather than
   the symlink.

   *Restrictions:* Must be an absolute path.

``target_scsi_id``
   SCSI id for the writer device.

   This value is optional for CD writers and is ignored for DVD writers.

   If you have configured your CD writer hardware to work through the
   normal filesystem device path, then you can leave this parameter
   unset. Cedar Backup will just use the target device (above) when
   talking to ``cdrecord``.

   Otherwise, if you have SCSI CD writer hardware or you have configured
   your non-SCSI hardware to operate like a SCSI device, then you need
   to provide Cedar Backup with a SCSI id it can use when talking with
   ``cdrecord``.

   For the purposes of Cedar Backup, a valid SCSI identifier must either
   be in the standard SCSI identifier form ``scsibus,target,lun`` or in
   the specialized-method form ``<method>:scsibus,target,lun``.

   An example of a standard SCSI identifier is ``1,6,2``. Today, the two
   most common examples of the specialized-method form are
   ``ATA:scsibus,target,lun`` and ``ATAPI:scsibus,target,lun``, but you
   may occassionally see other values (like ``OLDATAPI`` in some forks
   of ``cdrecord``).

   See *Configuring your Writer Device* for more information on writer devices
   and how they are configured.

   *Restrictions:* If set, must be a valid SCSI identifier.

``drive_speed``
   Speed of the drive, i.e. ``2`` for a 2x device.

   This field is optional. If it doesn't exist, the underlying
   device-related functionality will use the default drive speed.

   For DVD writers, it is best to leave this value unset, so
   ``growisofs`` can pick an appropriate speed. For CD writers, since
   media can be speed-sensitive, it is probably best to set a sensible
   value based on your specific writer and media.

   *Restrictions:* If set, must be an integer GE 1.

``check_data``
   Whether the media should be validated.

   This field indicates whether a resulting image on the media should be
   validated after the write completes, by running a consistency check
   against it. If this check is enabled, the contents of the staging
   directory are directly compared to the media, and an error is
   reported if there is a mismatch.

   Practice shows that some drives can encounter an error when writing a
   multisession disc, but not report any problems. This consistency
   check allows us to catch the problem. By default, the consistency
   check is disabled, but most users should choose to enable it unless
   they have a good reason not to.

   This field is optional. If it doesn't exist, then ``N`` will be
   assumed.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``check_media``
   Whether the media should be checked before writing to it.

   By default, Cedar Backup does not check its media before writing to
   it. It will write to any media in the backup device. If you set this
   flag to Y, Cedar Backup will make sure that the media has been
   initialized before writing to it. (Rewritable media is initialized
   using the initialize action.)

   If the configured media is not rewritable (like CD-R), then this
   behavior is modified slightly. For this kind of media, the check
   passes either if the media has been initialized *or* if the media
   appears unused.

   This field is optional. If it doesn't exist, then ``N`` will be
   assumed.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``warn_midnite``
   Whether to generate warnings for crossing midnite.

   This field indicates whether warnings should be generated if the
   store operation has to cross a midnite boundary in order to find data
   to write to disc. For instance, a warning would be generated if valid
   store data was only found in the day before or day after the current
   day.

   Configuration for some users is such that the store operation will
   always cross a midnite boundary, so they will not care about this
   warning. Other users will expect to never cross a boundary, and want
   to be notified that something “strange” might have happened.

   This field is optional. If it doesn't exist, then ``N`` will be
   assumed.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``no_eject``
   Indicates that the writer device should not be ejected.

   Under some circumstances, Cedar Backup ejects (opens and closes) the
   writer device. This is done because some writer devices need to
   re-load the media before noticing a media state change (like a new
   session).

   For most writer devices this is safe, because they have a tray that
   can be opened and closed. If your writer device does not have a tray
   *and* Cedar Backup does not properly detect this, then set this flag.
   Cedar Backup will not ever issue an eject command to your writer.

   *Note:* this could cause problems with your backup. For instance, with
   many writers, the check data step may fail if the media is not
   reloaded first. If this happens to you, you may need to get a
   different writer device.

   This field is optional. If it doesn't exist, then ``N`` will be
   assumed.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``refresh_media_delay``
   Number of seconds to delay after refreshing media

   This field is optional. If it doesn't exist, no delay will occur.

   Some devices seem to take a little while to stablize after refreshing
   the media (i.e. closing and opening the tray). During this period,
   operations on the media may fail. If your device behaves like this,
   you can try setting a delay of 10-15 seconds.

   *Restrictions:* If set, must be an integer GE 1.

``eject_delay``
   Number of seconds to delay after ejecting the tray

   This field is optional. If it doesn't exist, no delay will occur.

   If your system seems to have problems opening and closing the tray,
   one possibility is that the open/close sequence is happening too
   quickly --- either the tray isn't fully open when Cedar Backup
   tries to close it, or it doesn't report being open. To work around
   that problem, set an eject delay of a few seconds.

   *Restrictions:* If set, must be an integer GE 1.

``blank_behavior``
   Optimized blanking strategy.

   For more information about Cedar Backup's optimized blanking
   strategy, see :doc:`config`.

   This entire configuration section is optional. However, if you choose
   to provide it, you must configure both a blanking mode and a blanking
   factor.

   ``blank_mode``
      Blanking mode.

      *Restrictions:*\ Must be one of "daily" or "weekly".

   ``blank_factor``
      Blanking factor.

      *Restrictions:*\ Must be a floating point number GE 0.

.. _cedar-config-configfile-purge:

Purge Configuration
~~~~~~~~~~~~~~~~~~~

The purge configuration section contains configuration options related
the the purge action. This section contains a set of directories to be
purged, along with information about the schedule at which they should
be purged.

Typically, Cedar Backup should be configured to purge collect
directories daily (retain days of ``0``).

If you are tight on space, staging directories can also be purged daily.
However, if you have space to spare, you should consider purging about
once per week. That way, if your backup media is damaged, you will be
able to recreate the week's backup using the rebuild action.

You should also purge the working directory periodically, once every few
weeks or once per month. This way, if any unneeded files are left
around, perhaps because a backup was interrupted or because
configuration changed, they will eventually be removed. *The working
directory should not be purged any more frequently than once per week,
otherwise you will risk destroying data used for incremental backups.*

This is an example purge configuration section:

::

   <purge>
      <dir>
         <abs_path>/opt/backup/stage</abs_path>
         <retain_days>7</retain_days>
      </dir>
      <dir>
         <abs_path>/opt/backup/collect</abs_path>
         <retain_days>0</retain_days>
      </dir>
   </purge>
            

The following elements are part of the purge configuration section:

``dir``
   A directory to purge within.

   This is a subsection which contains information about a specific
   directory to purge within.

   This section can be repeated as many times as is necessary. At least
   one purge directory must be configured.

   The purge directory subsection contains the following fields:

   ``abs_path``
      Absolute path of the directory to purge within.

      The contents of the directory will be purged based on age. The
      purge will remove any files that were last modified more than
      “retain days” days ago. Empty directories will also eventually be
      removed. The purge directory itself will never be removed.

      The path may be either a directory, a soft link to a directory, or
      a hard link to a directory. Soft links *within* the directory (if
      any) are treated as files.

      *Restrictions:* Must be an absolute path.

   ``retain_days``
      Number of days to retain old files.

      Once it has been more than this many days since a file was last
      modified, it is a candidate for removal.

      *Restrictions:* Must be an integer GE 0.

.. _cedar-config-configfile-extensions:

Extensions Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

The extensions configuration section is used to configure third-party
extensions to Cedar Backup. If you don't intend to use any extensions,
or don't know what extensions are, then you can safely leave this
section out of your configuration file. It is optional.

Extensions configuration is used to specify “extended actions”
implemented by code external to Cedar Backup. An administrator can use
this section to map command-line Cedar Backup actions to third-party
extension functions.

Each extended action has a name, which is mapped to a Python function
within a particular module. Each action also has an index associated
with it. This index is used to properly order execution when more than
one action is specified on the command line. The standard actions have
predefined indexes, and extended actions are interleaved into the normal
order of execution using those indexes. The collect action has index
100, the stage index has action 200, the store action has index 300 and
the purge action has index 400.

   |warning|

   Extended actions should always be configured to run *before* the
   standard action they are associated with. This is because of the way
   indicator files are used in Cedar Backup. For instance, the staging
   process considers the collect action to be complete for a peer if the
   file ``cback.collect`` can be found in that peer's collect directory.

   If you were to run the standard collect action before your other
   collect-like actions, the indicator file would be written after the
   collect action completes but *before* all of the other actions even
   run. Because of this, there's a chance the stage process might back
   up the collect directory before the entire set of collect-like
   actions have completed --- and you would get no warning about this
   in your email!

So, imagine that a third-party developer provided a Cedar Backup
extension to back up a certain kind of database repository, and you
wanted to map that extension to the “database” command-line action. You
have been told that this function is called “foo.bar()”. You think of
this backup as a “collect” kind of action, so you want it to be
performed immediately before the collect action.

To configure this extension, you would list an action with a name
“database”, a module “foo”, a function name “bar” and an index of “99”.

This is how the hypothetical action would be configured:

::

   <extensions>
      <action>
         <name>database</name>
         <module>foo</module>
         <function>bar</function>
         <index>99</index>
      </action>
   </extensions>
            

The following elements are part of the extensions configuration section:

``action``
   This is a subsection that contains configuration related to a single
   extended action.

   This section can be repeated as many times as is necessary.

   The action subsection contains the following fields:

   ``name``
      Name of the extended action.

      *Restrictions:* Must be a non-empty string consisting of only
      lower-case letters and digits.

   ``module``
      Name of the Python module associated with the extension function.

      *Restrictions:* Must be a non-empty string and a valid Python
      identifier.

   ``function``
      Name of the Python extension function within the module.

      *Restrictions:* Must be a non-empty string and a valid Python
      identifier.

   ``index``
      Index of action, for execution ordering.

      *Restrictions:* Must be an integer GE 0.

.. _cedar-config-poolofone:

Setting up a Pool of One
------------------------

Cedar Backup has been designed primarily for situations where there is a
single master and a set of other clients that the master interacts with.
However, it will just as easily work for a single machine (a backup pool
of one).

Once you complete all of these configuration steps, your backups will
run as scheduled out of cron. Any errors that occur will be reported in
daily emails to your root user (or the user that receives root's email).
If you don't receive any emails, then you know your backup worked.

*Note:* all of these configuration steps should be run as the root user,
unless otherwise indicated.

   |tip|

   This setup procedure discusses how to set up Cedar Backup in the
   “normal case” for a pool of one. If you would like to modify the way
   Cedar Backup works (for instance, by ignoring the store stage and
   just letting your backup sit in a staging directory), you can do
   that. You'll just have to modify the procedure below based on
   information in the remainder of the manual.

Step 1: Decide when you will run your backup.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are four parts to a Cedar Backup run: collect, stage, store and
purge. The usual way of setting off these steps is through a set of cron
jobs. Although you won't create your cron jobs just yet, you should
decide now when you will run your backup so you are prepared for later.

Backing up large directories and creating ISO filesystem images can be
intensive operations, and could slow your computer down significantly.
Choose a backup time that will not interfere with normal use of your
computer. Usually, you will want the backup to occur every day, but it
is possible to configure cron to execute the backup only one day per
week, three days per week, etc.

   |warning|

   Because of the way Cedar Backup works, you must ensure that your
   backup *always* runs on the first day of your configured week. This
   is because Cedar Backup will only clear incremental backup
   information and re-initialize your media when running on the first
   day of the week. If you skip running Cedar Backup on the first day of
   the week, your backups will likely be “confused” until the next week
   begins, or until you re-run the backup using the ``--full`` flag.

Step 2: Make sure email works.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup relies on email for problem notification. This notification
works through the magic of cron. Cron will email any output from each
job it executes to the user associated with the job. Since by default
Cedar Backup only writes output to the terminal if errors occur, this
ensures that notification emails will only be sent out if errors occur.

In order to receive problem notifications, you must make sure that email
works for the user which is running the Cedar Backup cron jobs
(typically root). Refer to your distribution's documentation for
information on how to configure email on your system. Note that you may
prefer to configure root's email to forward to some other user, so you
do not need to check the root user's mail in order to see Cedar Backup
errors.

Step 3: Configure your writer device.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before using Cedar Backup, your writer device must be properly
configured. If you have configured your CD/DVD writer hardware to work
through the normal filesystem device path, then you just need to know
the path to the device on disk (something like ``/dev/cdrw``). Cedar
Backup will use the this device path both when talking to a command like
``cdrecord`` and when doing filesystem operations like running media
validation.

Your other option is to configure your CD writer hardware like a SCSI
device (either because it *is* a SCSI device or because you are using
some sort of interface that makes it look like one). In this case, Cedar
Backup will use the SCSI id when talking to ``cdrecord`` and the device
path when running filesystem operations.

See :doc:`config` for more information on writer devices and how they are
configured.

   |note|

   There is no need to set up your CD/DVD device if you have decided not
   to execute the store action.

   Due to the underlying utilities that Cedar Backup uses, the SCSI id
   may only be used for CD writers, *not* DVD writers.

Step 4: Configure your backup user.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose a user to be used for backups. Some platforms may come with a
“ready made” backup user. For other platforms, you may have to create a
user yourself. You may choose any id you like, but a descriptive name
such as ``backup`` or ``cback`` is a good choice. See your
distribution's documentation for information on how to add a user.

   |note|

   Standard Debian systems come with a user named ``backup``. You may
   choose to stay with this user or create another one.

Step 5: Create your backup tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup requires a backup directory tree on disk. This directory
tree must be roughly three times as big as the amount of data that will
be backed up on a nightly basis, to allow for the data to be collected,
staged, and then placed into an ISO filesystem image on disk. (This is
one disadvantage to using Cedar Backup in single-machine pools, but in
this day of really large hard drives, it might not be an issue.) Note
that if you elect not to purge the staging directory every night, you
will need even more space.

You should create a collect directory, a staging directory and a working
(temporary) directory. One recommended layout is this:

::

   /opt/
        backup/
               collect/
               stage/
               tmp/
            

If you will be backing up sensitive information (i.e. password files),
it is recommended that these directories be owned by the backup user
(whatever you named it), with permissions ``700``.

   |note|

   You don't have to use ``/opt`` as the root of your directory
   structure. Use anything you would like. I use ``/opt`` because it is
   my “dumping ground” for filesystems that Debian does not manage.

   Some users have requested that the Debian packages set up a more
   “standard” location for backups right out-of-the-box. I have resisted
   doing this because it's difficult to choose an appropriate backup
   location from within the package. If you would prefer, you can create
   the backup directory structure within some existing Debian directory
   such as ``/var/backups`` or ``/var/tmp``.

Step 6: Create the Cedar Backup configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following the instructions in *Configuration File Format* (above) create a
configuration file for your machine. Since you are working with a pool of one,
you must configure all four action-specific sections: collect, stage, store and
purge.

The usual location for the Cedar Backup config file is
``/etc/cback3.conf``. If you change the location, make sure you edit
your cronjobs (below) to point the ``cback3`` script at the correct
config file (using the ``--config`` option).

   |warning|

   Configuration files should always be writable only by root (or by the
   file owner, if the owner is not root).

   If you intend to place confidential information into the Cedar Backup
   configuration file, make sure that you set the filesystem permissions
   on the file appropriately. For instance, if you configure any
   extensions that require passwords or other similar information, you
   should make the file readable only to root or to the file owner (if
   the owner is not root).

Step 7: Validate the Cedar Backup configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the command ``cback3 validate`` to validate your configuration file.
This command checks that the configuration file can be found and parsed,
and also checks for typical configuration problems, such as invalid
CD/DVD device entries.

*Note:* the most common cause of configuration problems is in not closing
XML tags properly. Any XML tag that is “opened” must be “closed”
appropriately.

Step 8: Test your backup.
~~~~~~~~~~~~~~~~~~~~~~~~~

Place a valid CD/DVD disc in your drive, and then use the command
``cback3 --full all``. You should execute this command as root. If the
command completes with no output, then the backup was run successfully.

Just to be sure that everything worked properly, check the logfile
(``/var/log/cback3.log``) for errors and also mount the CD/DVD disc to
be sure it can be read.

*If Cedar Backup ever completes “normally” but the disc that is created is not
usable, please report this as a bug.  To be safe, always enable the consistency
check option in the store configuration section.* [4]_ 

Step 9: Modify the backup cron jobs.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Cedar Backup should be run as root, one way to configure the cron
job is to add a line like this to your ``/etc/crontab`` file:

::

   30 00 * * * root  cback3 all
            

Or, you can create an executable script containing just these lines and
place that file in the ``/etc/cron.daily`` directory:

::

   #/bin/sh
   cback3 all
            

You should consider adding the ``--output`` or ``-O`` switch to your
``cback3`` command-line in cron. This will result in larger logs, but
could help diagnose problems when commands like ``cdrecord`` or
``mkisofs`` fail mysteriously.

   |note|

   For general information about using cron, see the manpage for
   crontab(5).

   On a Debian system, execution of daily backups is controlled by the
   file ``/etc/cron.d/cedar-backup3``. As installed, this file contains
   several different settings, all commented out. Uncomment the “Single
   machine (pool of one)” entry in the file, and change the line so that
   the backup goes off when you want it to.

.. _cedar-config-client:

Setting up a Client Peer Node
-----------------------------

Cedar Backup has been designed to backup entire “pools” of machines. In
any given pool, there is one master and some number of clients. Most of
the work takes place on the master, so configuring a client is a little
simpler than configuring a master.

Backups are designed to take place over an RSH or SSH connection.
Because RSH is generally considered insecure, you are encouraged to use
SSH rather than RSH. This document will only describe how to configure
Cedar Backup to use SSH; if you want to use RSH, you're on your own.

Once you complete all of these configuration steps, your backups will
run as scheduled out of cron. Any errors that occur will be reported in
daily emails to your root user (or the user that receives root's email).
If you don't receive any emails, then you know your backup worked.

*Note:* all of these configuration steps should be run as the root user,
unless otherwise indicated.

   |note|

   See :doc:`securingssh` for some important notes on how to optionally further
   secure password-less SSH connections to your clients.

Step 1: Decide when you will run your backup.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are four parts to a Cedar Backup run: collect, stage, store and
purge. The usual way of setting off these steps is through a set of cron
jobs. Although you won't create your cron jobs just yet, you should
decide now when you will run your backup so you are prepared for later.

Backing up large directories and creating ISO filesystem images can be
intensive operations, and could slow your computer down significantly.
Choose a backup time that will not interfere with normal use of your
computer. Usually, you will want the backup to occur every day, but it
is possible to configure cron to execute the backup only one day per
week, three days per week, etc.

   |warning|

   Because of the way Cedar Backup works, you must ensure that your
   backup *always* runs on the first day of your configured week. This
   is because Cedar Backup will only clear incremental backup
   information and re-initialize your media when running on the first
   day of the week. If you skip running Cedar Backup on the first day of
   the week, your backups will likely be “confused” until the next week
   begins, or until you re-run the backup using the ``--full`` flag.

Step 2: Make sure email works.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup relies on email for problem notification. This notification
works through the magic of cron. Cron will email any output from each
job it executes to the user associated with the job. Since by default
Cedar Backup only writes output to the terminal if errors occur, this
neatly ensures that notification emails will only be sent out if errors
occur.

In order to receive problem notifications, you must make sure that email
works for the user which is running the Cedar Backup cron jobs
(typically root). Refer to your distribution's documentation for
information on how to configure email on your system. Note that you may
prefer to configure root's email to forward to some other user, so you
do not need to check the root user's mail in order to see Cedar Backup
errors.

Step 3: Configure the master in your backup pool.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will not be able to complete the client configuration until at least
step 3 of the master's configuration has been completed. In particular,
you will need to know the master's public SSH identity to fully
configure a client.

To find the master's public SSH identity, log in as the backup user on
the master and ``cat`` the public identity file ``~/.ssh/id_rsa.pub``:

::

   user@machine> cat ~/.ssh/id_rsa.pub
   ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEA0vOKjlfwohPg1oPRdrmwHk75l3mI9Tb/WRZfVnu2Pw69
   uyphM9wBLRo6QfOC2T8vZCB8o/ZIgtAM3tkM0UgQHxKBXAZ+H36TOgg7BcI20I93iGtzpsMA/uXQy8kH
   HgZooYqQ9pw+ZduXgmPcAAv2b5eTm07wRqFt/U84k6bhTzs= user@machine
            

Step 4: Configure your backup user.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose a user to be used for backups. Some platforms may come with a
"ready made" backup user. For other platforms, you may have to create a
user yourself. You may choose any id you like, but a descriptive name
such as ``backup`` or ``cback`` is a good choice. See your
distribution's documentation for information on how to add a user.

   |note|

   Standard Debian systems come with a user named ``backup``. You may
   choose to stay with this user or create another one.

Once you have created your backup user, you must create an SSH keypair
for it. Log in as your backup user, and then run the command
``ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa``:

::

   user@machine> ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
   Generating public/private rsa key pair.
   Created directory '/home/user/.ssh'.
   Your identification has been saved in /home/user/.ssh/id_rsa.
   Your public key has been saved in /home/user/.ssh/id_rsa.pub.
   The key fingerprint is:
   11:3e:ad:72:95:fe:96:dc:1e:3b:f4:cc:2c:ff:15:9e user@machine
            

The default permissions for this directory should be fine. However, if
the directory existed before you ran ``ssh-keygen``, then you may need
to modify the permissions. Make sure that the ``~/.ssh`` directory is
readable only by the backup user (i.e. mode ``700``), that the
``~/.ssh/id_rsa`` file is only readable and writable only by the backup
user (i.e. mode ``600``) and that the ``~/.ssh/id_rsa.pub`` file is
writable only by the backup user (i.e. mode ``600`` or mode ``644``).

Finally, take the master's public SSH identity (which you found in step
2) and cut-and-paste it into the file ``~/.ssh/authorized_keys``. Make
sure the identity value is pasted into the file *all on one line*, and
that the ``authorized_keys`` file is owned by your backup user and has
permissions ``600``.

If you have other preferences or standard ways of setting up your users'
SSH configuration (i.e. different key type, etc.), feel free to do
things your way. The important part is that the master must be able to
SSH into a client *with no password entry required*.

Step 5: Create your backup tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup requires a backup directory tree on disk. This directory
tree must be roughly as big as the amount of data that will be backed up
on a nightly basis (more if you elect not to purge it all every night).

You should create a collect directory and a working (temporary)
directory. One recommended layout is this:

::

   /opt/
        backup/
               collect/
               tmp/
            

If you will be backing up sensitive information (i.e. password files),
it is recommended that these directories be owned by the backup user
(whatever you named it), with permissions ``700``.

   |note|

   You don't have to use ``/opt`` as the root of your directory
   structure. Use anything you would like. I use ``/opt`` because it is
   my “dumping ground” for filesystems that Debian does not manage.

   Some users have requested that the Debian packages set up a more
   "standard" location for backups right out-of-the-box. I have resisted
   doing this because it's difficult to choose an appropriate backup
   location from within the package. If you would prefer, you can create
   the backup directory structure within some existing Debian directory
   such as ``/var/backups`` or ``/var/tmp``.

Step 6: Create the Cedar Backup configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following the instructions in *Configuration File Format* (above), create a
configuration file for your machine. Since you are working with a client, you
must configure all action-specific sections for the collect and purge actions.

The usual location for the Cedar Backup config file is
``/etc/cback3.conf``. If you change the location, make sure you edit
your cronjobs (below) to point the ``cback3`` script at the correct
config file (using the ``--config`` option).

   |warning|

   Configuration files should always be writable only by root (or by the
   file owner, if the owner is not root).

   If you intend to place confidental information into the Cedar Backup
   configuration file, make sure that you set the filesystem permissions
   on the file appropriately. For instance, if you configure any
   extensions that require passwords or other similar information, you
   should make the file readable only to root or to the file owner (if
   the owner is not root).

Step 7: Validate the Cedar Backup configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the command ``cback3 validate`` to validate your configuration file.
This command checks that the configuration file can be found and parsed,
and also checks for typical configuration problems. This command *only*
validates configuration on the one client, not the master or any other
clients in a pool.

*Note:* the most common cause of configuration problems is in not closing
XML tags properly. Any XML tag that is “opened” must be “closed”
appropriately.

Step 8: Test your backup.
~~~~~~~~~~~~~~~~~~~~~~~~~

Use the command ``cback3 --full collect purge``. If the command
completes with no output, then the backup was run successfully. Just to
be sure that everything worked properly, check the logfile
(``/var/log/cback3.log``) for errors.

Step 9: Modify the backup cron jobs.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Cedar Backup should be run as root, you should add a set of lines
like this to your ``/etc/crontab`` file:

::

   30 00 * * * root  cback3 collect
   30 06 * * * root  cback3 purge
            

You should consider adding the ``--output`` or ``-O`` switch to your
``cback3`` command-line in cron. This will result in larger logs, but
could help diagnose problems when commands like ``cdrecord`` or
``mkisofs`` fail mysteriously.

You will need to coordinate the collect and purge actions on the client
so that the collect action completes before the master attempts to
stage, and so that the purge action does not begin until after the
master has completed staging. Usually, allowing an hour or two between
steps should be sufficient.  [5]_

   |note|

   For general information about using cron, see the manpage for
   crontab(5).

   On a Debian system, execution of daily backups is controlled by the
   file ``/etc/cron.d/cedar-backup3``. As installed, this file contains
   several different settings, all commented out. Uncomment the “Client
   machine” entries in the file, and change the lines so that the backup
   goes off when you want it to.

.. _cedar-config-master:

Setting up a Master Peer Node
-----------------------------

Cedar Backup has been designed to backup entire “pools” of machines. In
any given pool, there is one master and some number of clients. Most of
the work takes place on the master, so configuring a master is somewhat
more complicated than configuring a client.

Backups are designed to take place over an RSH or SSH connection.
Because RSH is generally considered insecure, you are encouraged to use
SSH rather than RSH. This document will only describe how to configure
Cedar Backup to use SSH; if you want to use RSH, you're on your own.

Once you complete all of these configuration steps, your backups will
run as scheduled out of cron. Any errors that occur will be reported in
daily emails to your root user (or whichever other user receives root's
email). If you don't receive any emails, then you know your backup
worked.

*Note:* all of these configuration steps should be run as the root user,
unless otherwise indicated.

   |tip|

   This setup procedure discusses how to set up Cedar Backup in the
   “normal case” for a master. If you would like to modify the way Cedar
   Backup works (for instance, by ignoring the store stage and just
   letting your backup sit in a staging directory), you can do that.
   You'll just have to modify the procedure below based on information
   in the remainder of the manual.

Step 1: Decide when you will run your backup.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are four parts to a Cedar Backup run: collect, stage, store and
purge. The usual way of setting off these steps is through a set of cron
jobs. Although you won't create your cron jobs just yet, you should
decide now when you will run your backup so you are prepared for later.

Keep in mind that you do not necessarily have to run the collect action
on the master. See notes further below for more information.

Backing up large directories and creating ISO filesystem images can be
intensive operations, and could slow your computer down significantly.
Choose a backup time that will not interfere with normal use of your
computer. Usually, you will want the backup to occur every day, but it
is possible to configure cron to execute the backup only one day per
week, three days per week, etc.

   |warning|

   Because of the way Cedar Backup works, you must ensure that your
   backup *always* runs on the first day of your configured week. This
   is because Cedar Backup will only clear incremental backup
   information and re-initialize your media when running on the first
   day of the week. If you skip running Cedar Backup on the first day of
   the week, your backups will likely be “confused” until the next week
   begins, or until you re-run the backup using the ``--full`` flag.

Step 2: Make sure email works.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup relies on email for problem notification. This notification
works through the magic of cron. Cron will email any output from each
job it executes to the user associated with the job. Since by default
Cedar Backup only writes output to the terminal if errors occur, this
neatly ensures that notification emails will only be sent out if errors
occur.

In order to receive problem notifications, you must make sure that email
works for the user which is running the Cedar Backup cron jobs
(typically root). Refer to your distribution's documentation for
information on how to configure email on your system. Note that you may
prefer to configure root's email to forward to some other user, so you
do not need to check the root user's mail in order to see Cedar Backup
errors.

Step 3: Configure your writer device.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before using Cedar Backup, your writer device must be properly
configured. If you have configured your CD/DVD writer hardware to work
through the normal filesystem device path, then you just need to know
the path to the device on disk (something like ``/dev/cdrw``). Cedar
Backup will use the this device path both when talking to a command like
``cdrecord`` and when doing filesystem operations like running media
validation.

Your other option is to configure your CD writer hardware like a SCSI
device (either because it *is* a SCSI device or because you are using
some sort of interface that makes it look like one). In this case, Cedar
Backup will use the SCSI id when talking to ``cdrecord`` and the device
path when running filesystem operations.

See *Configuring your Writer Device* for more information on writer devices and
how they are configured.

   |note|

   There is no need to set up your CD/DVD device if you have decided not
   to execute the store action.

   Due to the underlying utilities that Cedar Backup uses, the SCSI id
   may only be used for CD writers, *not* DVD writers.

Step 4: Configure your backup user.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose a user to be used for backups. Some platforms may come with a
“ready made” backup user. For other platforms, you may have to create a
user yourself. You may choose any id you like, but a descriptive name
such as ``backup`` or ``cback`` is a good choice. See your
distribution's documentation for information on how to add a user.

   |note|

   Standard Debian systems come with a user named ``backup``. You may
   choose to stay with this user or create another one.

Once you have created your backup user, you must create an SSH keypair
for it. Log in as your backup user, and then run the command
``ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa``:

::

   user@machine> ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
   Generating public/private rsa key pair.
   Created directory '/home/user/.ssh'.
   Your identification has been saved in /home/user/.ssh/id_rsa.
   Your public key has been saved in /home/user/.ssh/id_rsa.pub.
   The key fingerprint is:
   11:3e:ad:72:95:fe:96:dc:1e:3b:f4:cc:2c:ff:15:9e user@machine
            

The default permissions for this directory should be fine. However, if
the directory existed before you ran ``ssh-keygen``, then you may need
to modify the permissions. Make sure that the ``~/.ssh`` directory is
readable only by the backup user (i.e. mode ``700``), that the
``~/.ssh/id_rsa`` file is only readable and writable by the backup user
(i.e. mode ``600``) and that the ``~/.ssh/id_rsa.pub`` file is writable
only by the backup user (i.e. mode ``600`` or mode ``644``).

If you have other preferences or standard ways of setting up your users'
SSH configuration (i.e. different key type, etc.), feel free to do
things your way. The important part is that the master must be able to
SSH into a client *with no password entry required*.

Step 5: Create your backup tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup requires a backup directory tree on disk. This directory
tree must be roughly large enough hold twice as much data as will be
backed up from the entire pool on a given night, plus space for whatever
is collected on the master itself. This will allow for all three
operations - collect, stage and store - to have enough space to
complete. Note that if you elect not to purge the staging directory
every night, you will need even more space.

You should create a collect directory, a staging directory and a working
(temporary) directory. One recommended layout is this:

::

   /opt/
        backup/
               collect/
               stage/
               tmp/
            

If you will be backing up sensitive information (i.e. password files),
it is recommended that these directories be owned by the backup user
(whatever you named it), with permissions ``700``.

   |note|

   You don't have to use ``/opt`` as the root of your directory
   structure. Use anything you would like. I use ``/opt`` because it is
   my “dumping ground” for filesystems that Debian does not manage.

   Some users have requested that the Debian packages set up a more
   “standard” location for backups right out-of-the-box. I have resisted
   doing this because it's difficult to choose an appropriate backup
   location from within the package. If you would prefer, you can create
   the backup directory structure within some existing Debian directory
   such as ``/var/backups`` or ``/var/tmp``.

Step 6: Create the Cedar Backup configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following the instructions in *Configuration File Foramt** (above), create a
configuration file for your machine. Since you are working with a master
machine, you would typically configure all four action-specific sections:
collect, stage, store and purge.

   |note|

   Note that the master can treat itself as a “client” peer for certain
   actions. As an example, if you run the collect action on the master,
   then you will stage that data by configuring a local peer
   representing the master.

   Something else to keep in mind is that you do not really have to run
   the collect action on the master. For instance, you may prefer to
   just use your master machine as a “consolidation point” machine that
   just collects data from the other client machines in a backup pool.
   In that case, there is no need to collect data on the master itself.

The usual location for the Cedar Backup config file is
``/etc/cback3.conf``. If you change the location, make sure you edit
your cronjobs (below) to point the ``cback3`` script at the correct
config file (using the ``--config`` option).

   |warning|

   Configuration files should always be writable only by root (or by the
   file owner, if the owner is not root).

   If you intend to place confidental information into the Cedar Backup
   configuration file, make sure that you set the filesystem permissions
   on the file appropriately. For instance, if you configure any
   extensions that require passwords or other similar information, you
   should make the file readable only to root or to the file owner (if
   the owner is not root).

Step 7: Validate the Cedar Backup configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the command ``cback3 validate`` to validate your configuration file.
This command checks that the configuration file can be found and parsed,
and also checks for typical configuration problems, such as invalid
CD/DVD device entries. This command *only* validates configuration on
the master, not any clients that the master might be configured to
connect to.

*Note:* the most common cause of configuration problems is in not closing
XML tags properly. Any XML tag that is “opened” must be “closed”
appropriately.

Step 8: Test connectivity to client machines.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step must wait until after your client machines have been at least
partially configured. Once the backup user(s) have been configured on
the client machine(s) in a pool, attempt an SSH connection to each
client.

Log in as the backup user on the master, and then use the command
``ssh user@machine`` where user is the name of backup user *on the
client machine*, and machine is the name of the client machine.

If you are able to log in successfully to each client without entering a
password, then things have been configured properly. Otherwise,
double-check that you followed the user setup instructions for the
master and the clients.

Step 9: Test your backup.
~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure that you have configured all of the clients in your backup
pool. On all of the clients, execute ``cback3 --full collect``. (You will
probably have already tested this command on each of the clients, so it should
succeed.)

When all of the client backups have completed, place a valid CD/DVD disc
in your drive, and then use the command ``cback3 --full all``. You should
execute this command as root. If the command completes with no output, then the
backup was run successfully.

Just to be sure that everything worked properly, check the logfile
(``/var/log/cback3.log``) on the master and each of the clients, and
also mount the CD/DVD disc on the master to be sure it can be read.

You may also want to run ``cback3 purge`` on the master and each client
once you have finished validating that everything worked.

*If Cedar Backup ever completes “normally” but the disc that is created
is not usable, please report this as a bug. To be safe, always enable
the consistency check option in the store configuration section.*

Step 10: Modify the backup cron jobs.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Cedar Backup should be run as root, you should add a set of lines
like this to your ``/etc/crontab`` file:

::

   30 00 * * * root  cback3 collect
   30 02 * * * root  cback3 stage
   30 04 * * * root  cback3 store
   30 06 * * * root  cback3 purge
            

You should consider adding the ``--output`` or ``-O`` switch to your
``cback3`` command-line in cron. This will result in larger logs, but
could help diagnose problems when commands like ``cdrecord`` or
``mkisofs`` fail mysteriously.

You will need to coordinate the collect and purge actions on clients so
that their collect actions complete before the master attempts to stage,
and so that their purge actions do not begin until after the master has
completed staging. Usually, allowing an hour or two between steps should
be sufficient.

   |note|

   For general information about using cron, see the manpage for
   crontab(5).

   On a Debian system, execution of daily backups is controlled by the
   file ``/etc/cron.d/cedar-backup3``. As installed, this file contains
   several different settings, all commented out. Uncomment the “Master
   machine” entries in the file, and change the lines so that the backup
   goes off when you want it to.

.. _cedar-config-writer:

Configuring your Writer Device
------------------------------

Device Types
~~~~~~~~~~~~

In order to execute the store action, you need to know how to identify
your writer device. Cedar Backup supports two kinds of device types: CD
writers and DVD writers. DVD writers are always referenced through a
filesystem device name (i.e. ``/dev/dvd``). CD writers can be referenced
either through a SCSI id, or through a filesystem device name. Which you
use depends on your operating system and hardware.

Devices identified by by device name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For all DVD writers, and for CD writers on certain platforms, you will
configure your writer device using only a device name. If your writer
device works this way, you should just specify <target_device> in
configuration. You can either leave <target_scsi_id> blank or remove it
completely. The writer device will be used both to write to the device
and for filesystem operations --- for instance, when the media needs
to be mounted to run the consistency check.

Devices identified by SCSI id
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cedar Backup can use devices identified by SCSI id only when configured
to use the ``cdwriter`` device type.

In order to use a SCSI device with Cedar Backup, you must know both the
SCSI id <target_scsi_id> and the device name <target_device>. The SCSI
id will be used to write to media using ``cdrecord``; and the device
name will be used for other filesystem operations.

A true SCSI device will always have an address ``scsibus,target,lun``
(i.e. ``1,6,2``). This should hold true on most UNIX-like systems
including Linux and the various BSDs (although I do not have a BSD
system to test with currently). The SCSI address represents the location
of your writer device on the one or more SCSI buses that you have
available on your system.

On some platforms, it is possible to reference non-SCSI writer devices
(i.e. an IDE CD writer) using an emulated SCSI id. If you have
configured your non-SCSI writer device to have an emulated SCSI id,
provide the filesystem device path in <target_device> and the SCSI id in
<target_scsi_id>, just like for a real SCSI device.

You should note that in some cases, an emulated SCSI id takes the same
form as a normal SCSI id, while in other cases you might see a method
name prepended to the normal SCSI id (i.e. “ATA:1,1,1”).

Linux Notes
~~~~~~~~~~~

On a Linux system, IDE writer devices often have a emulated SCSI
address, which allows SCSI-based software to access the device through
an IDE-to-SCSI interface. Under these circumstances, the first IDE
writer device typically has an address ``0,0,0``. However, support for
the IDE-to-SCSI interface has been deprecated and is not well-supported
in newer kernels (kernel 2.6.x and later).

Newer Linux kernels can address ATA or ATAPI drives without SCSI
emulation by prepending a “method” indicator to the emulated device
address. For instance, ``ATA:0,0,0`` or ``ATAPI:0,0,0`` are typical
values.

However, even this interface is deprecated as of late 2006, so with
relatively new kernels you may be better off using the filesystem device
path directly rather than relying on any SCSI emulation.

Here are some hints about how to find your Linux CD writer hardware.
First, try to reference your device using the filesystem device path:

::

   cdrecord -prcap dev=/dev/cdrom
            

Running this command on my hardware gives output that looks like this
(just the top few lines):

::

   Device type    : Removable CD-ROM
   Version        : 0
   Response Format: 2
   Capabilities   : 
   Vendor_info    : 'LITE-ON '
   Identification : 'DVDRW SOHW-1673S'
   Revision       : 'JS02'
   Device seems to be: Generic mmc2 DVD-R/DVD-RW.

   Drive capabilities, per MMC-3 page 2A:
            

If this works, and the identifying information at the top of the output
looks like your CD writer device, you've probably found a working
configuration. Place the device path into <target_device> and leave
<target_scsi_id> blank.

If this doesn't work, you should try to find an ATA or ATAPI device:

::

   cdrecord -scanbus dev=ATA
   cdrecord -scanbus dev=ATAPI
            

On my development system, I get a result that looks something like this
for ATA:

::

   scsibus1:
           1,0,0   100) 'LITE-ON ' 'DVDRW SOHW-1673S' 'JS02' Removable CD-ROM
           1,1,0   101) *
           1,2,0   102) *
           1,3,0   103) *
           1,4,0   104) *
           1,5,0   105) *
           1,6,0   106) *
           1,7,0   107) *
            

Again, if you get a result that you recognize, you have again probably
found a working configuraton. Place the associated device path (in my
case, ``/dev/cdrom``) into <target_device> and put the emulated SCSI id
(in this case, ``ATA:1,0,0``) into <target_scsi_id>.

Any further discussion of how to configure your CD writer hardware is
outside the scope of this document. If you have tried the hints above
and still can't get things working, you may want to reference the Linux
CDROM HOWTO (`<http://www.tldp.org/HOWTO/CDROM-HOWTO>`__) or the ATA
RAID HOWTO (`<http://www.tldp.org/HOWTO/ATA-RAID-HOWTO/index.html>`__)
for more information.

Mac OS X Notes
~~~~~~~~~~~~~~

On a Mac OS X (darwin) system, things get strange. Apple has abandoned
traditional SCSI device identifiers in favor of a system-wide resource
id. So, on a Mac, your writer device will have a name something like
``IOCompactDiscServices`` (for a CD writer) or ``IODVDServices`` (for a
DVD writer). If you have multiple drives, the second drive probably has
a number appended, i.e. ``IODVDServices/2`` for the second DVD writer.
You can try to figure out what the name of your device is by grepping
through the output of the command ``ioreg -l``. [6]_

Unfortunately, even if you can figure out what device to use, I can't
really support the store action on this platform. In OS X, the
“automount” function of the Finder interferes significantly with Cedar
Backup's ability to mount and unmount media and write to the CD or DVD
hardware. The Cedar Backup writer and image functionality does work on
this platform, but the effort required to fight the operating system
about who owns the media and the device makes it nearly impossible to
execute the store action successfully.

.. _cedar-config-blanking:

Optimized Blanking Stategy
--------------------------

When the optimized blanking strategy has not been configured, Cedar
Backup uses a simplistic approach: rewritable media is blanked at the
beginning of every week, period.

Since rewritable media can be blanked only a finite number of times
before becoming unusable, some users --- especially users of
rewritable DVD media with its large capacity --- may prefer to blank
the media less often.

If the optimized blanking strategy is configured, Cedar Backup will use
a blanking factor and attempt to determine whether future backups will
fit on the current media. If it looks like backups will fit, then the
media will not be blanked.

This feature will only be useful (assuming single disc is used for the
whole week's backups) if the estimated total size of the weekly backup
is considerably smaller than the capacity of the media (no more than 50%
of the total media capacity), and only if the size of the backup can be
expected to remain fairly constant over time (no frequent rapid growth
expected).

There are two blanking modes: daily and weekly. If the weekly blanking
mode is set, Cedar Backup will only estimate future capacity (and
potentially blank the disc) once per week, on the starting day of the
week. If the daily blanking mode is set, Cedar Backup will estimate
future capacity (and potentially blank the disc) every time it is run.
*You should only use the daily blanking mode in conjunction with daily
collect configuration, otherwise you will risk losing data.*

If you are using the daily blanking mode, you can typically set the
blanking value to 1.0. This will cause Cedar Backup to blank the media
whenever there is not enough space to store the current day's backup.

If you are using the weekly blanking mode, then finding the correct
blanking factor will require some experimentation. Cedar Backup
estimates future capacity based on the configured blanking factor. The
disc will be blanked if the following relationship is true:

::

   bytes available / (1 + bytes required) LE blanking factor
         

Another way to look at this is to consider the blanking factor as a sort
of (upper) backup growth estimate:

::

   Total size of weekly backup / Full backup size at the start of the week
         

This ratio can be estimated using a week or two of previous backups. For
instance, take this example, where March 10 is the start of the week and
March 4 through March 9 represent the incremental backups from the
previous week:

::

   /opt/backup/staging# du -s 2007/03/*
   3040    2007/03/01
   3044    2007/03/02
   6812    2007/03/03
   3044    2007/03/04
   3152    2007/03/05
   3056    2007/03/06
   3060    2007/03/07
   3056    2007/03/08
   4776    2007/03/09
   6812    2007/03/10
   11824   2007/03/11
         

In this case, the ratio is approximately 4:

::

   6812 + (3044 + 3152 + 3056 + 3060 + 3056 + 4776) / 6812 = 3.9571
         

To be safe, you might choose to configure a factor of 5.0.

Setting a higher value reduces the risk of exceeding media capacity
mid-week but might result in blanking the media more often than is
necessary.

If you run out of space mid-week, then the solution is to run the
rebuild action. If this happens frequently, a higher blanking factor
value should be used.

----------

*Previous*: :doc:`commandline` • *Next*: :doc:`extensions`

----------

.. [1]
   See `<http://www.xml.com/pub/a/98/10/guide0.html>`__ for a basic
   introduction to XML.

.. [2]
   See :doc:`basic`

.. [3]
   See `<http://docs.python.org/lib/re-syntax.html>`__

.. [4]
   See `<https://github.com/pronovic/cedar-backup3/issues>`__.

.. [5]
   See :doc:`basic`

.. [6]
   Thanks to the file README.macosX in the cdrtools-2.01+01a01 source
   tree for this information

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
