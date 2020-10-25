.. _cedar-extensions:

Official Extensions
===================

.. _cedar-extensions-sysinfo:

System Information Extension
----------------------------

The System Information Extension is a simple Cedar Backup extension used
to save off important system recovery information that might be useful
when reconstructing a “broken” system. It is intended to be run either
immediately before or immediately after the standard collect action.

This extension saves off the following information to the configured
Cedar Backup collect directory. Saved off data is always compressed
using ``bzip2``.

-  Currently-installed Debian packages via ``dpkg --get-selections``

-  Disk partition information via ``fdisk -l``

-  System-wide mounted filesystem contents, via ``ls -laR``

The Debian-specific information is only collected on systems where
``/usr/bin/dpkg`` exists.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>sysinfo</name>
         <module>CedarBackup3.extend.sysinfo</module>
         <function>executeAction</function>
         <index>99</index>
      </action>
   </extensions>
         

This extension relies on the options and collect configuration sections
in the standard Cedar Backup configuration file, but requires no new
configuration of its own.

.. _cedar-extensions-amazons3:

Amazon S3 Extension
-------------------

The Amazon S3 extension writes data to Amazon S3 cloud storage rather
than to physical media. It is intended to replace the store action, but
you can also use it alongside the store action if you'd prefer to backup
your data in more than one place. This extension must be run after the
stage action.

The underlying functionality relies on the `AWS
CLI <http://aws.amazon.com/documentation/cli/>`__ toolset. Before you
use this extension, you need to set up your Amazon S3 account and
configure AWS CLI as detailed in Amazon's `setup
guide <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html>`__.
The extension assumes that the backup is being executed as root, and
switches over to the configured backup user to run the ``aws`` program.
So, make sure you configure the AWS CLI tools as the backup user and not
root. (This is different than the ``cback-amazons3-sync`` tool, which
executes AWS CLI command as the same user that is running the tool.)

You can use whichever Amazon-supported authentication mechanism you
would like when setting up connectivity for the AWS CLI. It's best to
set up a separate user in the `IAM
Console <https://console.aws.amazon.com/iam/home>`__ rather than using
your main administrative user.

You probably want to lock down this user so that it can only take backup
related actions in the AWS infrastructure. One option is to apply the
``AmazonS3FullAccess`` policy, which grants full access to the S3
infrastructure. If you would like to lock down the user even further,
this appears to be the minimum set of permissions required for Cedar
Backup, written as a JSON policy statement:

::

   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:ListBucket",
                   "s3:ListObjects",
                   "s3:PutObject",
                   "s3:PutObjectAcl",
                   "s3:DeleteObject"
               ],
               "Resource": [
                   "arn:aws:s3:::my-bucket",
                   "arn:aws:s3:::my-bucket/*"
               ]
           }
       ]
   }
         

In the ``Resource`` section, be sure to list the name of your S3 bucket
instead of ``my-bucket``.

When using physical media via the standard store action, there is an
implicit limit to the size of a backup, since a backup must fit on a
single disc. Since there is no physical media, no such limit exists for
Amazon S3 backups. This leaves open the possibility that Cedar Backup
might construct an unexpectedly-large backup that the administrator is
not aware of. Over time, this might become expensive, either in terms of
network bandwidth or in terms of Amazon S3 storage and I/O charges. To
mitigate this risk, set a reasonable maximum size using the
configuration elements shown below. If the backup fails, you have a
chance to review what made the backup larger than you expected, and you
can either correct the problem (i.e. remove a large temporary directory
that got inadvertently included in the backup) or change configuration
to take into account the new "normal" maximum size.

You can optionally configure Cedar Backup to encrypt data before sending
it to S3. To do that, provide a complete command line using the
``${input}`` and ``${output}`` variables to represent the original input
file and the encrypted output file. This command will be executed as the
backup user.

For instance, you can use something like this with GPG:

::

   /usr/bin/gpg -c --no-use-agent --batch --yes --passphrase-file /home/backup/.passphrase -o ${output} ${input}
         

The GPG mechanism depends on a strong passphrase for security. One way
to generate a strong passphrase is using your system random number
generator, i.e.:

::

   dd if=/dev/urandom count=20 bs=1 | xxd -ps
         

(See
`StackExchange <http://security.stackexchange.com/questions/14867/gpg-encryption-security>`__
for more details about that advice.) If you decide to use encryption,
make sure you save off the passphrase in a safe place, so you can get at
your backup data later if you need to. And obviously, make sure to set
permissions on the passphrase file so it can only be read by the backup
user.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>amazons3</name>
         <module>CedarBackup3.extend.amazons3</module>
         <function>executeAction</function>
         <index>201</index> <!-- just after stage -->
      </action>
   </extensions>
         

This extension relies on the options and staging configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``amazons3`` configuration section. This is an example
configuration section with encryption disabled:

::

   <amazons3>
         <s3_bucket>example.com-backup/staging</s3_bucket>
   </amazons3>
         

The following elements are part of the Amazon S3 configuration section:

``warn_midnite``
   Whether to generate warnings for crossing midnite.

   This field indicates whether warnings should be generated if the
   Amazon S3 operation has to cross a midnite boundary in order to find
   data to write to the cloud. For instance, a warning would be
   generated if valid data was only found in the day before or day after
   the current day.

   Configuration for some users is such that the amazons3 operation will
   always cross a midnite boundary, so they will not care about this
   warning. Other users will expect to never cross a boundary, and want
   to be notified that something “strange” might have happened.

   This field is optional. If it doesn't exist, then ``N`` will be
   assumed.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``s3_bucket``
   The name of the Amazon S3 bucket that data will be written to.

   This field configures the S3 bucket that your data will be written
   to. In S3, buckets are named globally. For uniqueness, you would
   typically use the name of your domain followed by some suffix, such
   as ``example.com-backup``. If you want, you can specify a
   subdirectory within the bucket, such as
   ``example.com-backup/staging``.

   *Restrictions:* Must be non-empty.

``encrypt``
   Command used to encrypt backup data before upload to S3

   If this field is provided, then data will be encrypted before it is
   uploaded to Amazon S3. You must provide the entire command used to
   encrypt a file, including the ``${input}`` and ``${output}``
   variables. An example GPG command is shown above, but you can use any
   mechanism you choose. The command will be run as the configured
   backup user.

   *Restrictions:* If provided, must be non-empty.

``full_size_limit``
   Maximum size of a full backup

   If this field is provided, then a size limit will be applied to full
   backups. If the total size of the selected staging directory is
   greater than the limit, then the backup will fail.

   You can enter this value in two different forms. It can either be a
   simple number, in which case the value is assumed to be in bytes; or
   it can be a number followed by a unit (KB, MB, GB).

   Valid examples are “10240”, “250 MB” or “1.1 GB”.

   *Restrictions:* Must be a value as described above, greater than
   zero.

``incr_size_limit``
   Maximum size of an incremental backup

   If this field is provided, then a size limit will be applied to
   incremental backups. If the total size of the selected staging
   directory is greater than the limit, then the backup will fail.

   You can enter this value in two different forms. It can either be a
   simple number, in which case the value is assumed to be in bytes; or
   it can be a number followed by a unit (KB, MB, GB).

   Valid examples are “10240”, “250 MB” or “1.1 GB”.

   *Restrictions:* Must be a value as described above, greater than
   zero.

.. _cedar-extensions-subversion:

Subversion Extension
--------------------

The Subversion Extension is a Cedar Backup extension used to back up
`Subversion <http://subversion.org>`__ version control repositories via the Cedar Backup
command line. It is intended to be run either immediately before or
immediately after the standard collect action.

Each configured Subversion repository can be backed using the same
collect modes allowed for filesystems in the standard Cedar Backup
collect action (weekly, daily, incremental) and the output can be
compressed using either ``gzip`` or ``bzip2``.

There are two different kinds of Subversion repositories at this
writing: BDB (Berkeley Database) and FSFS (a "filesystem within a
filesystem"). This extension backs up both kinds of repositories in the
same way, using ``svnadmin dump`` in an incremental mode.

It turns out that FSFS repositories can also be backed up just like any
other filesystem directory. If you would rather do the backup that way,
then use the normal collect action rather than this extension. If you
decide to do that, be sure to consult the Subversion documentation and
make sure you understand the limitations of this kind of backup.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>subversion</name>
         <module>CedarBackup3.extend.subversion</module>
         <function>executeAction</function>
         <index>99</index>
      </action>
   </extensions>
         

This extension relies on the options and collect configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``subversion`` configuration section. This is an example
Subversion configuration section:

::

   <subversion>
      <collect_mode>incr</collect_mode>
      <compress_mode>bzip2</compress_mode>
      <repository>
         <abs_path>/opt/public/svn/docs</abs_path>
      </repository>
      <repository>
         <abs_path>/opt/public/svn/web</abs_path>
         <compress_mode>gzip</compress_mode>
      </repository>
      <repository_dir>
         <abs_path>/opt/private/svn</abs_path>
         <collect_mode>daily</collect_mode>
      </repository_dir>
   </subversion>
         

The following elements are part of the Subversion configuration section:

``collect_mode``
   Default collect mode.

   The collect mode describes how frequently a Subversion repository is
   backed up. The Subversion extension recognizes the same collect modes
   as the standard Cedar Backup collect action (see
   :doc:`basic`).

   This value is the collect mode that will be used by default during
   the backup process. Individual repositories (below) may override this
   value. If *all* individual repositories provide their own value, then
   this default value may be omitted from configuration.

   *Note:* if your backup device does not suppport multisession discs,
   then you should probably use the ``daily`` collect mode to avoid
   losing data.

   *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

``compress_mode``
   Default compress mode.

   Subversion repositories backups are just specially-formatted text
   files, and often compress quite well using ``gzip`` or ``bzip2``. The
   compress mode describes how the backed-up data will be compressed, if
   at all.

   This value is the compress mode that will be used by default during
   the backup process. Individual repositories (below) may override this
   value. If *all* individual repositories provide their own value, then
   this default value may be omitted from configuration.

   *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

``repository``
   A Subversion repository be collected.

   This is a subsection which contains information about a specific
   Subversion repository to be backed up.

   This section can be repeated as many times as is necessary. At least
   one repository or repository directory must be configured.

   The ``repository`` subsection contains the following fields:

   ``collect_mode``
      Collect mode for this repository.

      This field is optional. If it doesn't exist, the backup will use
      the default collect mode.

      *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

   ``compress_mode``
      Compress mode for this repository.

      This field is optional. If it doesn't exist, the backup will use
      the default compress mode.

      *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

   ``abs_path``
      Absolute path of the Subversion repository to back up.

      *Restrictions:* Must be an absolute path.

``repository_dir``
   A Subversion parent repository directory be collected.

   This is a subsection which contains information about a Subversion
   parent repository directory to be backed up. Any subdirectory
   immediately within this directory is assumed to be a Subversion
   repository, and will be backed up.

   This section can be repeated as many times as is necessary. At least
   one repository or repository directory must be configured.

   The ``repository_dir`` subsection contains the following fields:

   ``collect_mode``
      Collect mode for this repository.

      This field is optional. If it doesn't exist, the backup will use
      the default collect mode.

      *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

   ``compress_mode``
      Compress mode for this repository.

      This field is optional. If it doesn't exist, the backup will use
      the default compress mode.

      *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

   ``abs_path``
      Absolute path of the Subversion repository to back up.

      *Restrictions:* Must be an absolute path.

   ``exclude``
      List of paths or patterns to exclude from the backup.

      This is a subsection which contains a set of paths and patterns to
      be excluded within this subversion parent directory.

      This section is entirely optional, and if it exists can also be
      empty.

      The exclude subsection can contain one or more of each of the
      following fields:

      ``rel_path``
         A relative path to be excluded from the backup.

         The path is assumed to be relative to the subversion parent
         directory itself. For instance, if the configured subversion
         parent directory is ``/opt/svn`` a configured relative path of
         ``software`` would exclude the path ``/opt/svn/software``.

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be non-empty.

      ``pattern``
         A pattern to be excluded from the backup.

         The pattern must be a Python regular expression. It is assumed
         to be bounded at front and back by the beginning and end of the
         string (i.e. it is treated as if it begins with ``^`` and ends
         with ``$``).

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be non-empty

.. _cedar-extensions-mysql:

MySQL Extension
---------------

The MySQL Extension is a Cedar Backup extension used to back up
`MySQL <http://www.mysql.com>`__ databases via the Cedar Backup command line. It
is intended to be run either immediately before or immediately after the
standard collect action.

   |note|

   This extension always produces a full backup. There is currently no
   facility for making incremental backups. If/when someone has a need
   for this and can describe how to do it, I will update this extension
   or provide another.

The backup is done via the ``mysqldump`` command included with the MySQL
product. Output can be compressed using ``gzip`` or ``bzip2``.
Administrators can configure the extension either to back up all
databases or to back up only specific databases.

The extension assumes that all configured databases can be backed up by
a single user. Often, the “root” database user will be used. An
alternative is to create a separate MySQL “backup” user and grant that
user rights to read (but not write) various databases as needed. This
second option is probably your best choice.

   |warning|

   The extension accepts a username and password in configuration.
   However, you probably do not want to list those values in Cedar
   Backup configuration. This is because Cedar Backup will provide these
   values to ``mysqldump`` via the command-line ``--user`` and
   ``--password`` switches, which will be visible to other users in the
   process listing.

   Instead, you should configure the username and password in one of
   MySQL's configuration files. Typically, that would be done by putting
   a stanza like this in ``/root/.my.cnf``:

   ::

      [mysqldump]
      user     = root
      password = <secret>
               

   Of course, if you are executing the backup as a user other than root,
   then you would create the file in that user's home directory instead.

   As a side note, it is also possible to configure ``.my.cnf`` such
   that Cedar Backup can back up a remote database server:

   ::

      [mysqldump]
      host = remote.host
               

   For this to work, you will also need to grant privileges properly for
   the user which is executing the backup. See your MySQL documentation
   for more information about how this can be done.

   Regardless of whether you are using ``~/.my.cnf`` or
   ``/etc/cback3.conf`` to store database login and password
   information, you should be careful about who is allowed to view that
   information. Typically, this means locking down permissions so that
   only the file owner can read the file contents (i.e. use mode
   ``0600``).

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>mysql</name>
         <module>CedarBackup3.extend.mysql</module>
         <function>executeAction</function>
         <index>99</index>
      </action>
   </extensions>
         

This extension relies on the options and collect configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``mysql`` configuration section. This is an example MySQL
configuration section:

::

   <mysql>
      <compress_mode>bzip2</compress_mode>
      <all>Y</all>
   </mysql>
         

If you have decided to configure login information in Cedar Backup
rather than using MySQL configuration, then you would add the username
and password fields to configuration:

::

   <mysql>
      <user>root</user>
      <password>password</password>
      <compress_mode>bzip2</compress_mode>
      <all>Y</all>
   </mysql>
         

The following elements are part of the MySQL configuration section:

``user``
   Database user.

   The database user that the backup should be executed as. Even if you
   list more than one database (below) all backups must be done as the
   same user. Typically, this would be ``root`` (i.e. the database root
   user, not the system root user).

   This value is optional. You should probably configure the username
   and password in MySQL configuration instead, as discussed above.

   *Restrictions:* If provided, must be non-empty.

``password``
   Password associated with the database user.

   This value is optional. You should probably configure the username
   and password in MySQL configuration instead, as discussed above.

   *Restrictions:* If provided, must be non-empty.

``compress_mode``
   Compress mode.

   MySQL databases dumps are just specially-formatted text files, and
   often compress quite well using ``gzip`` or ``bzip2``. The compress
   mode describes how the backed-up data will be compressed, if at all.

   *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

``all``
   Indicates whether to back up all databases.

   If this value is ``Y``, then all MySQL databases will be backed up.
   If this value is ``N``, then one or more specific databases must be
   specified (see below).

   If you choose this option, the entire database backup will go into
   one big dump file.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``database``
   Named database to be backed up.

   If you choose to specify individual databases rather than all
   databases, then each database will be backed up into its own dump
   file.

   This field can be repeated as many times as is necessary. At least
   one database must be configured if the all option (above) is set to
   ``N``. You may not configure any individual databases if the all
   option is set to ``Y``.

   *Restrictions:* Must be non-empty.

.. _cedar-extensions-postgresql:

PostgreSQL Extension
--------------------

This is a community-contributed extension provided by Antoine Beaupre
("The Anarcat"). I have added regression tests around the configuration
parsing code and I will maintain this section in the user manual based
on his source code documentation.

The PostgreSQL Extension is a Cedar Backup extension used to back up
`PostgreSQL <http://www.postgresql.org>`__  databases via the Cedar Backup
command line. It is intended to be run either immediately before or immediately
after the standard collect action.

The backup is done via the ``pg_dump`` or ``pg_dumpall`` commands
included with the PostgreSQL product. Output can be compressed using
``gzip`` or ``bzip2``. Administrators can configure the extension either
to back up all databases or to back up only specific databases.

The extension assumes that the current user has passwordless access to
the database since there is no easy way to pass a password to the
``pg_dump`` client. This can be accomplished using appropriate
configuration in the ``pg_hda.conf`` file.

This extension always produces a full backup. There is currently no
facility for making incremental backups.

   |warning|

   Once you place PostgreSQL configuration into the Cedar Backup
   configuration file, you should be careful about who is allowed to see
   that information. This is because PostgreSQL configuration will
   contain information about available PostgreSQL databases and
   usernames. Typically, you might want to lock down permissions so that
   only the file owner can read the file contents (i.e. use mode
   ``0600``).

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>postgresql</name>
         <module>CedarBackup3.extend.postgresql</module>
         <function>executeAction</function>
         <index>99</index>
      </action>
   </extensions>
         

This extension relies on the options and collect configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``postgresql`` configuration section. This is an example
PostgreSQL configuration section:

::

   <postgresql>
      <compress_mode>bzip2</compress_mode>
      <user>username</user>
      <all>Y</all>
   </postgresql>
         

If you decide to back up specific databases, then you would list them
individually, like this:

::

   <postgresql>
      <compress_mode>bzip2</compress_mode>
      <user>username</user>
      <all>N</all>
      <database>db1</database>
      <database>db2</database>
   </postgresql>
         

The following elements are part of the PostgreSQL configuration section:

``user``
   Database user.

   The database user that the backup should be executed as. Even if you
   list more than one database (below) all backups must be done as the
   same user.

   This value is optional.

   Consult your PostgreSQL documentation for information on how to
   configure a default database user outside of Cedar Backup, and for
   information on how to specify a database password when you configure
   a user within Cedar Backup. You will probably want to modify
   ``pg_hda.conf``.

   *Restrictions:* If provided, must be non-empty.

``compress_mode``
   Compress mode.

   PostgreSQL databases dumps are just specially-formatted text files,
   and often compress quite well using ``gzip`` or ``bzip2``. The
   compress mode describes how the backed-up data will be compressed, if
   at all.

   *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

``all``
   Indicates whether to back up all databases.

   If this value is ``Y``, then all PostgreSQL databases will be backed
   up. If this value is ``N``, then one or more specific databases must
   be specified (see below).

   If you choose this option, the entire database backup will go into
   one big dump file.

   *Restrictions:* Must be a boolean (``Y`` or ``N``).

``database``
   Named database to be backed up.

   If you choose to specify individual databases rather than all
   databases, then each database will be backed up into its own dump
   file.

   This field can be repeated as many times as is necessary. At least
   one database must be configured if the all option (above) is set to
   ``N``. You may not configure any individual databases if the all
   option is set to ``Y``.

   *Restrictions:* Must be non-empty.

.. _cedar-extensions-mbox:

Mbox Extension
--------------

The Mbox Extension is a Cedar Backup extension used to incrementally
back up UNIX-style “mbox” mail folders via the Cedar Backup command
line. It is intended to be run either immediately before or immediately
after the standard collect action.

Mbox mail folders are not well-suited to being backed up by the normal
Cedar Backup incremental backup process. This is because active folders
are typically appended to on a daily basis. This forces the incremental
backup process to back them up every day in order to avoid losing data.
This can result in quite a bit of wasted space when backing up large
mail folders.

The Mbox extension leverages the ``grepmail`` utility to back up only email
messages which have been received since the last incremental backup. This way,
even if a folder is added to every day, only the recently-added messages are
is backed up. This can potentially save a lot of space.

Each configured mbox file or directory can be backed using the same
collect modes allowed for filesystems in the standard Cedar Backup
collect action (weekly, daily, incremental) and the output can be
compressed using either ``gzip`` or ``bzip2``.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>mbox</name>
         <module>CedarBackup3.extend.mbox</module>
         <function>executeAction</function>
         <index>99</index>
      </action>
   </extensions>
         

This extension relies on the options and collect configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``mbox`` configuration section. This is an example mbox
configuration section:

::

   <mbox>
      <collect_mode>incr</collect_mode>
      <compress_mode>gzip</compress_mode>
      <file>
         <abs_path>/home/user1/mail/greylist</abs_path>
         <collect_mode>daily</collect_mode>
      </file>
      <dir>
         <abs_path>/home/user2/mail</abs_path>
      </dir>
      <dir>
         <abs_path>/home/user3/mail</abs_path>
         <exclude>
            <rel_path>spam</rel_path>
            <pattern>.*debian.*</pattern>
         </exclude>
      </dir>
   </mbox>
         

Configuration is much like the standard collect action. Differences come
from the fact that mbox directories are *not* collected recursively.

Unlike collect configuration, exclusion information can only be
configured at the mbox directory level (there are no global exclusions).
Another difference is that no absolute exclusion paths are allowed ---
only relative path exclusions and patterns.

The following elements are part of the mbox configuration section:

``collect_mode``
   Default collect mode.

   The collect mode describes how frequently an mbox file or directory
   is backed up. The mbox extension recognizes the same collect modes as
   the standard Cedar Backup collect action (see
   :doc:`basic`).

   This value is the collect mode that will be used by default during
   the backup process. Individual files or directories (below) may
   override this value. If *all* individual files or directories provide
   their own value, then this default value may be omitted from
   configuration.

   *Note:* if your backup device does not suppport multisession discs,
   then you should probably use the ``daily`` collect mode to avoid
   losing data.

   *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

``compress_mode``
   Default compress mode.

   Mbox file or directory backups are just text, and often compress
   quite well using ``gzip`` or ``bzip2``. The compress mode describes
   how the backed-up data will be compressed, if at all.

   This value is the compress mode that will be used by default during
   the backup process. Individual files or directories (below) may
   override this value. If *all* individual files or directories provide
   their own value, then this default value may be omitted from
   configuration.

   *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

``file``
   An individual mbox file to be collected.

   This is a subsection which contains information about an individual
   mbox file to be backed up.

   This section can be repeated as many times as is necessary. At least
   one mbox file or directory must be configured.

   The file subsection contains the following fields:

   ``collect_mode``
      Collect mode for this file.

      This field is optional. If it doesn't exist, the backup will use
      the default collect mode.

      *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

   ``compress_mode``
      Compress mode for this file.

      This field is optional. If it doesn't exist, the backup will use
      the default compress mode.

      *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

   ``abs_path``
      Absolute path of the mbox file to back up.

      *Restrictions:* Must be an absolute path.

``dir``
   An mbox directory to be collected.

   This is a subsection which contains information about an mbox
   directory to be backed up. An mbox directory is a directory
   containing mbox files. Every file in an mbox directory is assumed to
   be an mbox file. Mbox directories are *not* collected recursively.
   Only the files immediately within the configured directory will be
   backed-up and any subdirectories will be ignored.

   This section can be repeated as many times as is necessary. At least
   one mbox file or directory must be configured.

   The dir subsection contains the following fields:

   ``collect_mode``
      Collect mode for this file.

      This field is optional. If it doesn't exist, the backup will use
      the default collect mode.

      *Restrictions:* Must be one of ``daily``, ``weekly`` or ``incr``.

   ``compress_mode``
      Compress mode for this file.

      This field is optional. If it doesn't exist, the backup will use
      the default compress mode.

      *Restrictions:* Must be one of ``none``, ``gzip`` or ``bzip2``.

   ``abs_path``
      Absolute path of the mbox directory to back up.

      *Restrictions:* Must be an absolute path.

   ``exclude``
      List of paths or patterns to exclude from the backup.

      This is a subsection which contains a set of paths and patterns to
      be excluded within this mbox directory.

      This section is entirely optional, and if it exists can also be
      empty.

      The exclude subsection can contain one or more of each of the
      following fields:

      ``rel_path``
         A relative path to be excluded from the backup.

         The path is assumed to be relative to the mbox directory
         itself. For instance, if the configured mbox directory is
         ``/home/user2/mail`` a configured relative path of ``SPAM``
         would exclude the path ``/home/user2/mail/SPAM``.

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be non-empty.

      ``pattern``
         A pattern to be excluded from the backup.

         The pattern must be a Python regular expression. It is assumed
         to be bounded at front and back by the beginning and end of the
         string (i.e. it is treated as if it begins with ``^`` and ends
         with ``$``).

         This field can be repeated as many times as is necessary.

         *Restrictions:* Must be non-empty

.. _cedar-extensions-encrypt:

Encrypt Extension
-----------------

The Encrypt Extension is a Cedar Backup extension used to encrypt
backups. It does this by encrypting the contents of a master's staging
directory each day after the stage action is run. This way, backed-up
data is encrypted both when sitting on the master and when written to
disc. This extension must be run before the standard store action,
otherwise unencrypted data will be written to disc.

There are several differents ways encryption could have been built in to
or layered on to Cedar Backup. I asked the mailing list for opinions on
the subject in January 2007 and did not get a lot of feedback, so I
chose the option that was simplest to understand and simplest to
implement. If other encryption use cases make themselves known in the
future, this extension can be enhanced or replaced.

Currently, this extension supports only GPG. However, it would be
straightforward to support other public-key encryption mechanisms, such
as OpenSSL.

   |warning|

   If you decide to encrypt your backups, be *absolutely sure* that you
   have your GPG secret key saved off someplace safe --- someplace
   other than on your backup disc. If you lose your secret key, your
   backup will be useless.

   I suggest that before you rely on this extension, you should execute
   a dry run and make sure you can successfully decrypt the backup that
   is written to disc.

Before configuring the Encrypt extension, you must configure GPG. Either
create a new keypair or use an existing one. Determine which user will
execute your backup (typically root) and have that user import *and
lsign* the public half of the keypair. Then, save off the secret half of
the keypair someplace safe, apart from your backup (i.e. on a floppy
disk or USB drive). Make sure you know the recipient name associated
with the public key because you'll need it to configure Cedar Backup.
(If you can run ``gpg -e -r "Recipient Name" file.txt`` and it executes
cleanly with no user interaction required, you should be OK.)

An encrypted backup has the same file structure as a normal backup, so
all of the instructions in :doc:`recovering` apply. The only
difference is that encrypted files will have an additional ``.gpg``
extension (so for instance ``file.tar.gz`` becomes ``file.tar.gz.gpg``).
To recover decrypted data, simply log on as a user which has access to
the secret key and decrypt the ``.gpg`` file that you are interested in.
Then, recover the data as usual.

*Note:* I am being intentionally vague about how to configure and use GPG,
because I do not want to encourage neophytes to blindly use this
extension. If you do not already understand GPG well enough to follow
the two paragraphs above, *do not use this extension*. Instead, before
encrypting your backups, check out the excellent GNU Privacy Handbook at
`<http://www.gnupg.org/gph/en/manual.html>`__ and gain an understanding
of how encryption can help you or hurt you.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions>
      <action>
         <name>encrypt</name>
         <module>CedarBackup3.extend.encrypt</module>
         <function>executeAction</function>
         <index>301</index>
      </action>
   </extensions>
         

This extension relies on the options and staging configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``encrypt`` configuration section. This is an example Encrypt
configuration section:

::

   <encrypt>
      <encrypt_mode>gpg</encrypt_mode>
      <encrypt_target>Backup User</encrypt_target>
   </encrypt>
         

The following elements are part of the Encrypt configuration section:

``encrypt_mode``
   Encryption mode.

   This value specifies which encryption mechanism will be used by the
   extension.

   Currently, only the GPG public-key encryption mechanism is supported.

   *Restrictions:* Must be ``gpg``.

``encrypt_target``
   Encryption target.

   The value in this field is dependent on the encryption mode. For the
   ``gpg`` mode, this is the name of the recipient whose public key will
   be used to encrypt the backup data, i.e. the value accepted by
   ``gpg -r``.

.. _cedar-extensions-split:

Split Extension
---------------

The Split Extension is a Cedar Backup extension used to split up large
files within staging directories. It is probably only useful in
combination with the ``cback3-span`` command, which requires individual
files within staging directories to each be smaller than a single disc.

You would normally run this action immediately after the standard stage
action, but you could also choose to run it by hand immediately before
running ``cback3-span``.

The split extension uses the standard UNIX ``split`` tool to split the
large files up. This tool simply splits the files on bite-size
boundaries. It has no knowledge of file formats.

*Note: this means that in order to recover the data in your original
large file, you must have every file that the original file was split
into.* Think carefully about whether this is what you want. It doesn't
sound like a huge limitation. However, ``cback3-span`` might put an
indivdual file on *any* disc in a set --- the files split from one
larger file will not necessarily be together. That means you will
probably need every disc in your backup set in order to recover any data
from the backup set.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions> 
      <action>
         <name>split</name>
         <module>CedarBackup3.extend.split</module>
         <function>executeAction</function>
         <index>299</index>
      </action>
   </extensions>
         

This extension relies on the options and staging configuration sections
in the standard Cedar Backup configuration file, and then also requires
its own ``split`` configuration section. This is an example Split
configuration section:

::

   <split>
      <size_limit>250 MB</size_limit>
      <split_size>100 MB</split_size>
   </split>
         

The following elements are part of the Split configuration section:

``size_limit``
   Size limit.

   Files with a size strictly larger than this limit will be split by
   the extension.

   You can enter this value in two different forms. It can either be a
   simple number, in which case the value is assumed to be in bytes; or
   it can be a number followed by a unit (KB, MB, GB).

   Valid examples are “10240”, “250 MB” or “1.1 GB”.

   *Restrictions:* Must be a size as described above.

``split_size``
   Split size.

   This is the size of the chunks that a large file will be split into.
   The final chunk may be smaller if the split size doesn't divide
   evenly into the file size.

   You can enter this value in two different forms. It can either be a
   simple number, in which case the value is assumed to be in bytes; or
   it can be a number followed by a unit (KB, MB, GB).

   Valid examples are “10240”, “250 MB” or “1.1 GB”.

   *Restrictions:* Must be a size as described above.

.. _cedar-extensions-capacity:

Capacity Extension
------------------

The capacity extension checks the current capacity of the media in the
writer and prints a warning if the media exceeds an indicated capacity.
The capacity is indicated either by a maximum percentage utilized or by
a minimum number of bytes that must remain unused.

This action can be run at any time, but is probably best run as the last
action on any given day, so you get as much notice as possible that your
media is full and needs to be replaced.

To enable this extension, add the following section to the Cedar Backup
configuration file:

::

   <extensions> <action>
         <name>capacity</name>
         <module>CedarBackup3.extend.capacity</module>
         <function>executeAction</function>
         <index>299</index>
      </action>
   </extensions>
         

This extension relies on the options and store configuration sections in
the standard Cedar Backup configuration file, and then also requires its
own ``capacity`` configuration section. This is an example Capacity
configuration section that configures the extension to warn if the media
is more than 95.5% full:

::

   <capacity>
      <max_percentage>95.5</max_percentage>
   </capacity>
         

This example configures the extension to warn if the media has fewer
than 16 MB free:

::

   <capacity>
      <min_bytes>16 MB</min_bytes>
   </capacity>
         

The following elements are part of the Capacity configuration section:

``max_percentage``
   Maximum percentage of the media that may be utilized.

   You must provide either this value *or* the ``min_bytes`` value.

   *Restrictions:* Must be a floating point number between 0.0 and 100.0

``min_bytes``
   Minimum number of free bytes that must be available.

   You can enter this value in two different forms. It can either be a
   simple number, in which case the value is assumed to be in bytes; or
   it can be a number followed by a unit (KB, MB, GB).

   Valid examples are “10240”, “250 MB” or “1.1 GB”.

   You must provide either this value *or* the ``max_percentage`` value.

   *Restrictions:* Must be a byte quantity as described above.

----------

*Previous*: :doc:`config` • *Next*: :doc:`extenspec`

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
