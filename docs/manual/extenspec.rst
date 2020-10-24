.. _cedar-extenspec:

Extension Architecture Interface
================================

The Cedar Backup Extension Architecture Interface is the application
programming interface used by third-party developers to write Cedar
Backup extensions. This appendix briefly specifies the interface in
enough detail for someone to succesfully implement an extension.

Backup extensions are third-party pieces of code which extend Cedar Backup's
functionality. Extensions can be invoked from the Cedar Backup command line and
are allowed to place their configuration in Cedar Backup's configuration file.

There is a one-to-one mapping between a command-line extended action and
an extension function. The mapping is configured in the Cedar Backup
configuration file using a section something like this:

::

   <extensions>
      <action>
         <name>database</name>
         <module>foo</module>
         <function>bar</function>
         <index>101</index>
      </action> 
   </extensions>
         

In this case, the action “database” has been mapped to the extension
function ``foo.bar()``.

Extension functions can take any actions they would like to once they
have been invoked, but must abide by these rules:

1. Extensions must not write to ``stdout`` or ``stderr`` using functions
   such as ``print`` or ``sys.write``.

2. All logging must take place using the Python logging facility.
   Flow-of-control logging should happen on the ``CedarBackup3.log``
   topic. Authors can assume that ERROR will always go to the terminal,
   that INFO and WARN will always be logged, and that DEBUG will be
   ignored unless debugging is enabled.

3. Any time an extension invokes a command-line utility, it must be done
   through the ``CedarBackup3.util.executeCommand`` function. This will
   help keep Cedar Backup safer from format-string attacks, and will
   make it easier to consistently log command-line process output.

4. Extensions may not return any value.

5. Extensions must throw a Python exception containing a descriptive
   message if processing fails. Extension authors can use their
   judgement as to what constitutes failure; however, any problems
   during execution should result in either a thrown exception or a
   logged message.

6. Extensions may rely only on Cedar Backup functionality that is
   advertised as being part of the public interface. This means that
   extensions must not directly make use of methods, functions or values
   starting with with the ``_`` character. Furthermore, extensions
   should only rely on parts of the public interface that are documented
   in the online interface documentation.

7. Extension authors are encouraged to extend the Cedar Backup public
   interface through normal methods of inheritence. However, no
   extension is allowed to directly change Cedar Backup code in a way
   that would affect how Cedar Backup itself executes when the extension
   has not been invoked. For instance, extensions would not be allowed
   to add new command-line options or new writer types.

8. Extensions must be written to assume an empty locale set (no
   ``$LC_*`` settings) and ``$LANG=C``. For the typical open-source
   software project, this would imply writing output-parsing code
   against the English localization (if any). The ``executeCommand``
   function does sanitize the environment to enforce this configuration.

Extension functions take three arguments: the path to configuration on
disk, a ``CedarBackup3.cli.Options`` object representing the
command-line options in effect, and a ``CedarBackup3.config.Config``
object representing parsed standard configuration.

::

   def function(configPath, options, config):
      """Sample extension function."""
      pass
         

This interface is structured so that simple extensions can use standard
configuration without having to parse it for themselves, but more
complicated extensions can get at the configuration file on disk and
parse it again as needed.

The interface to the ``CedarBackup3.cli.Options`` and
``CedarBackup3.config.Config`` classes has been thoroughly documented
in the online interface documentation.  The interface is guaranteed to change
only in backwards-compatible ways unless the Cedar Backup major version number
is bumped (i.e. from 3 to 4).

If an extension needs to add its own configuration information to the
Cedar Backup configuration file, this extra configuration must be added
in a new configuration section using a name that does not conflict with
standard configuration or other known extensions.

For instance, our hypothetical database extension might require
configuration indicating the path to some repositories to back up. This
information might go into a section something like this:

::

   <database>
      <repository>/path/to/repo1</repository>
      <repository>/path/to/repo2</repository>
   </database>
         

In order to read this new configuration, the extension code can either
inherit from the ``Config`` object and create a subclass that knows how
to parse the new ``database`` config section, or can write its own code
to parse whatever it needs out of the file. Either way, the resulting
code is completely independent of the standard Cedar Backup
functionality.

----------

*Previous*: :doc:`extensions` • *Next*: :doc:`depends`

.. |note| image:: images/note.png
.. |tip| image:: images/tip.png
.. |warning| image:: images/warning.png
