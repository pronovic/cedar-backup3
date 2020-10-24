.. _cedar-preface:

Preface
=======

.. _cedar-preface-purpose:

Purpose
-------

This software manual has been written to document version 2 and version 3 of
Cedar Backup.  Version 2 was first released in 2005, and version 3 in 2015.

.. _cedar-preface-audience:

Audience
--------

This manual has been written for computer-literate administrators who
need to use and configure Cedar Backup on their Linux or UNIX-like
system. The examples in this manual assume the reader is relatively
comfortable with UNIX and command-line interfaces.

.. _cedar-preface-conventions:

Conventions Used in This Book
-----------------------------

This section covers the various conventions used in this manual.

Typographic Conventions
~~~~~~~~~~~~~~~~~~~~~~~

*Term*
   Used for first use of important terms.

``Command``
   Used for commands, command output, and switches

*Replaceable*
   Used for replaceable items in code and text

``Filenames``
   Used for file and directory names

.. _cedar-preface-conventions-typo:

Icons
~~~~~

|note| This icon designates a note relating to the surrounding text.

|tip| This icon designates a helpful tip relating to the surrounding text.

|warning| This icon designates a warning relating to the surrounding text.

.. _cedar-preface-organization:

Organization of This Manual
---------------------------

:doc:`intro`
   Provides some some general history about Cedar Backup, what needs it
   is intended to meet, how to get support, and how to migrate from
   version 2 to version 3.

:doc:`basic`:
   Discusses the basic concepts of a Cedar Backup infrastructure, and
   specifies terms used throughout the rest of the manual.

:doc:`install`
   Explains how to install Cedar Backup either from the Debian package or from
   the Python package.

:doc:`commandline`:
   Discusses the various Cedar Backup command-line tools, including the
   primary ``cback3`` command.

:doc:`config`:
   Provides detailed information about how to configure Cedar Backup.

:doc:`extensions`
   Describes each of the officially-supported Cedar Backup extensions.

:doc:`extenspec`
   Specifies the Cedar Backup extension architecture interface, through
   which third party developers can write extensions to Cedar Backup.

:doc:`depends`
   Provides some additional information about the packages which Cedar
   Backup relies on, including information about how to find
   documentation and packages on non-Debian systems.

:doc:`recovering`
   Cedar Backup provides no facility for restoring backups, assuming the
   administrator can handle this infrequent task. This appendix provides
   some notes for administrators to work from.

:doc:`securingssh`
   Password-less SSH connections are a necessary evil when remote backup
   processes need to execute without human interaction. This appendix
   describes some ways that you can reduce the risk to your backup pool
   should your master machine be compromised.

*Next*: :doc:`intro`

.. |note| image:: images/note.png 
.. |tip| image:: images/tip.png 
.. |warning| image:: images/warning.png 

