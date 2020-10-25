.. _cedar-securingssh:

Securing Password-less SSH Connections
======================================

Cedar Backup relies on password-less public key SSH connections to make
various parts of its backup process work. Password-less ``scp`` is used
to stage files from remote clients to the master, and password-less
``ssh`` is used to execute actions on managed clients.

Normally, it is a good idea to avoid password-less SSH connections in
favor of using an SSH agent. The SSH agent manages your SSH connections
so that you don't need to type your passphrase over and over. You get
most of the benefits of a password-less connection without the risk.
Unfortunately, because Cedar Backup has to execute without human
involvement (through a cron job), use of an agent really isn't feasable.
We have to rely on true password-less public keys to give the master
access to the client peers.

Traditionally, Cedar Backup has relied on a “segmenting” strategy to
minimize the risk. Although the backup typically runs as root --- so
that all parts of the filesystem can be backed up --- we don't use the
root user for network connections. Instead, we use a dedicated backup
user on the master to initiate network connections, and dedicated users
on each of the remote peers to accept network connections.

With this strategy in place, an attacker with access to the backup user
on the master (or even root access, really) can at best only get access
to the backup user on the remote peers. We still concede a local attack
vector, but at least that vector is restricted to an unprivileged user.

Some Cedar Backup users may not be comfortable with this risk, and
others may not be able to implement the segmentation strategy --- they
simply may not have a way to create a login which is only used for
backups.

So, what are these users to do? Fortunately there is a solution. The SSH
authorized keys file supports a way to put a “filter” in place on an SSH
connection. This excerpt is from the AUTHORIZED_KEYS FILE FORMAT section
of man 8 sshd:

::

   command="command"
      Specifies that the command is executed whenever this key is used for
      authentication.  The command supplied by the user (if any) is ignored.  The
      command is run on a pty if the client requests a pty; otherwise it is run
      without a tty.  If an 8-bit clean channel is required, one must not request
      a pty or should specify no-pty.  A quote may be included in the command by
      quoting it with a backslash.  This option might be useful to restrict
      certain public keys to perform just a specific operation.  An example might
      be a key that permits remote backups but nothing else.  Note that the client
      may specify TCP and/or X11 forwarding unless they are explicitly prohibited.
      Note that this option applies to shell, command or subsystem execution.
         

Essentially, this gives us a way to authenticate the commands that are
being executed. We can either accept or reject commands, and we can even
provide a readable error message for commands we reject. The filter is
applied on the remote peer, to the key that provides the master access
to the remote peer.

So, let's imagine that we have two hosts: master “mickey”, and peer
“minnie”. Here is the original ``~/.ssh/authorized_keys`` file for the
backup user on minnie (remember, this is all on one line in the file):

::

   ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEAxw7EnqVULBFgPcut3WYp3MsSpVB9q9iZ+awek120391k;mm0c221=3=km
   =m=askdalkS82mlF7SusBTcXiCk1BGsg7axZ2sclgK+FfWV1Jm0/I9yo9FtAZ9U+MmpL901231asdkl;ai1-923ma9s=9=
   1-2341=-a0sd=-sa0=1z= backup@mickey
         

This line is the public key that minnie can use to identify the backup
user on mickey. Assuming that there is no passphrase on the private key
back on mickey, the backup user on mickey can get direct access to
minnie.

To put the filter in place, we add a command option to the key, like
this:

::

   command="/opt/backup/validate-backup" ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEAxw7EnqVULBFgPcut3WYp
   3MsSpVB9q9iZ+awek120391k;mm0c221=3=km=m=askdalkS82mlF7SusBTcXiCk1BGsg7axZ2sclgK+FfWV1Jm0/I9yo9F
   tAZ9U+MmpL901231asdkl;ai1-923ma9s=9=1-2341=-a0sd=-sa0=1z= backup@mickey
         

Basically, the command option says that whenever this key is used to
successfully initiate a connection, the ``/opt/backup/validate-backup``
command will be run *instead of* the real command that came over the SSH
connection. Fortunately, the interface gives the command access to
certain shell variables that can be used to invoke the original command
if you want to.

A very basic ``validate-backup`` script might look something like this:

::

   #!/bin/bash
   if [[ "${SSH_ORIGINAL_COMMAND}" == "ls -l" ]] ; then
       ${SSH_ORIGINAL_COMMAND}
   else
      echo "Security policy does not allow command [${SSH_ORIGINAL_COMMAND}]."
      exit 1
   fi
         

This script allows exactly ``ls -l`` and nothing else. If the user
attempts some other command, they get a nice error message telling them
that their command has been disallowed.

For remote commands executed over ``ssh``, the original command is
exactly what the caller attempted to invoke. For remote copies, the
commands are either ``scp -f file`` (copy *from* the peer to the master)
or ``scp -t file`` (copy *to* the peer from the master).

If you want, you can see what command SSH thinks it is executing by
using ``ssh -v`` or ``scp -v``. The command will be right at the top,
something like this:

::

   Executing: program /usr/bin/ssh host mickey, user (unspecified), command scp -v -f .profile
   OpenSSH_4.3p2 Debian-9, OpenSSL 0.9.8c 05 Sep 2006
   debug1: Reading configuration data /home/backup/.ssh/config
   debug1: Applying options for daystrom
   debug1: Reading configuration data /etc/ssh/ssh_config
   debug1: Applying options for *
   debug2: ssh_connect: needpriv 0
         

Omit the ``-v`` and you have your command: ``scp -f .profile``.

For a normal, non-managed setup, you need to allow the following
commands, where ``/path/to/collect/`` is replaced with the real path to
the collect directory on the remote peer:

::

   scp -f /path/to/collect/cback.collect
   scp -f /path/to/collect/*
   scp -t /path/to/collect/cback.stage
         

If you are configuring a managed client, then you also need to list the
exact command lines that the master will be invoking on the managed
client. You are guaranteed that the master will invoke one action at a
time, so if you list two lines per action (full and non-full) you should
be fine. Here's an example for the collect action:

::

   /usr/bin/cback3 --full collect
   /usr/bin/cback3 collect
         
Of course, you would have to list the actual path to the ``cback3``
executable --- exactly the one listed in the ``<cback_command>``
configuration option for your managed peer.

Below is the script that I use for my own backups, to allow the
master to stage files from each client.  This is stored as 
``~/.ssh/validate-backup`` and is referenced in ``~/.ssh/authorized-keys``
as described above.

::

   # Since this script is specified as the command in ~/.ssh/authorized_keys, it
   # acts as a "filter" and prevents the backup user from doing anything except
   # specific Cedar Backup actions (stage, in this case, via scp).

   # See the AUTHORIZED_KEYS FILE FORMAT section in sshd(8) for more information.

   typeset -x COLLECTDIR=/data/backup/collect

   typeset -x CMD1="scp -f ${COLLECTDIR}/cback.collect"    # check collect indicator
   typeset -x CMD2="scp -f ${COLLECTDIR}/*"                # stage all files
   typeset -x CMD3="scp -t ${COLLECTDIR}/cback.stage"      # write the stage indicator

   if [[ "${SSH_ORIGINAL_COMMAND}" == "${CMD1}" ]] ; then
       ${SSH_ORIGINAL_COMMAND}
   elif [[ "${SSH_ORIGINAL_COMMAND}" == "${CMD2}" ]]; then
      ${SSH_ORIGINAL_COMMAND}
   elif [[ "${SSH_ORIGINAL_COMMAND}" == "${CMD3}" ]]; then
      ${SSH_ORIGINAL_COMMAND}
   else
      echo "Security policy does not allow command [${SSH_ORIGINAL_COMMAND}]."
      exit 1
   fi


I hope that there is enough information here for interested users to implement
something that makes them comfortable. 

----------

*Previous*: :doc:`recovering` • *Next*: :doc:`copyright`

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
