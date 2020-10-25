# Developer Notes

## Development Environment

This code has been around since the early 2000s.  Historically, my development
environment has been Vim on Debian Linux.  Recently, I've also begun using
IntelliJ on MacOS.  As of now, I do not do any software development on Windows
it's not clear whether it works there. (I haven't tried using it on Windows
since ~2005.)

## Packaging and Dependencies

This project uses [Poetry](https://python-poetry.org/) to manage Python packaging and dependencies.  Most day-to-day tasks (such as running unit tests from the command line) are orchestrated through Poetry.  

A coding standard is enforced using [Black](https://github.com/psf/black), [isort](https://pypi.org/project/isort/) and [Pylint](https://www.pylint.org/).

## Pre-Commit Hooks

We rely on pre-commit hooks to ensure that the code is properly-formatted,
clean, and type-safe when it's checked in.  The `run install` step described
below installs the project pre-commit hooks into your repository.  These hooks
are configured in [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

If necessary, you can temporarily disable a hook using Git's `--no-verify`
switch.  However, keep in mind that the CI build on GitHub enforces these
checks, so the build will fail.

## Prequisites

Nearly all prerequisites are managed by Poetry.  All you need to do is make
sure that you have a working Python 3 enviroment and install Poetry itself.  

### MacOS

On MacOS, it's easiest to use [Homebrew](https://brew.sh/):

```
$ brew install python3
$ brew install poetry
```

When you're done, you probably want to set up your profile so the `python` on
your `$PATH` is Python 3 from Homebrew (in `/usr/local`).  By default, you'll
get the standard Python 2 that comes with MacOS.

### Debian

First, install Python 3 and related tools:

```
$ sudo apt-get install python3 python3-venv python3-pip
```

Once that's done, make sure Python 3 is the default on your system.  There are
a couple of ways to do this, but using `update-alternatives` as discussed 
on [StackOverflow](https://unix.stackexchange.com/a/410851) is probably 
the best.

Then, install Poetry in your home directory:

```
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

## Configure Poetry's Python Interpreter

At this point, you can either let Poetry use its defaults, or tell it explicity
which Python interpreter you want it to use.  On MacOS anyway, Poetry >= v1.1.3
seems to be quite aggressive about using the most recent version of Python
available on my system (even if it's not on my `$PATH`), which is not always
what I want.

To force Poetry to use a particular version of Python on the `$PATH`, do this:

```
$ poetry env use 3.8
```

To force Poetry to use a version that isn't on the `$PATH`, you can't just use
the version number as shown above.  You have to provide the whole path:

```
$ poetry env use /usr/local/Cellar/python@3.9/3.9.0/bin/python3.9
```

You can check the version that is in use with:

```
$ poetry env info
```

If you switch between versions, it is a good idea to sanity check what is
actually being used.  I've noticed that if I start on 3.8 and then switch to
3.9 (in the order shown above), then `python env info` still reports Python
3.8.6 when I'm done.  The fix seems to be to remove the virutalenvs and start
over:

```
$ poetry env list
$ poetry env remove <item>
```

For more background, see [this discussion](https://github.com/python-poetry/poetry/issues/522) and also [Poetry PR #731](https://github.com/python-poetry/poetry/pull/731).

## Activating the Virtual Environment

Poetry manages the virtual environment used for testing.  Theoretically, the
Poetry `shell` command gives you a shell using that virtualenv.  However, it
doesn't work that well.  Instead, it's simpler to just activate the virtual
environment directly.  The [`run`](run) script has an entry that dumps out the
correct `source` command. Otherwise, see [`notes/venv.sh`](notes/venv.sh) for a way
to set up a global alias that activates any virtualenv found in the current
directory.

## Developer Tasks

The [`run`](run) script provides shortcuts for common developer tasks:

```
$ run --help

------------------------------------
Shortcuts for common developer tasks
------------------------------------

Usage: run <command>

- run install: Setup the virtualenv via Poetry and install pre-commit hooks
- run activate: Print command needed to activate the Poetry virtualenv
- run requirements: Regenerate the docs/requirements.txt file
- run checks: Run the PyLint code checker
- run format: Run the code formatters
- run diagnostics: Print diagnostics about the Cedar Backup runtime environment
- run test: Run the unit test suite
- run tox: Run the broader Tox test suite used by the GitHub CI action
- run docs: Build the Spinx documentation for cedar-backup3.readthedocs.io
- run docs -o: Build the Spinx documentation and open in a browser
- run release: Release a specific version and tag the code
- run publish: Publish the current code to PyPI and push to GitHub

Try 'run test --help' to get a list of other arguments accepted by that command.

To run scripts, use poetry directly: 

- poetry run cback3
- poetry run cback3-amazons3-sync
- poetry run cback3-span

These are the exact scripts published by Poetry as part of the Python package.
```

## Integration with IntelliJ or PyCharm

For my day-to-day IDE, I often use IntelliJ Ultimate with the Python plugin
installed, which is basically equivalent to PyCharm. By integrating Black and
Pylint, most everything important that can be done from a shell environment can
also be done right in IntelliJ.

Unfortunately, it is somewhat difficult to provide a working IntelliJ
configuration that other developers can simply import. There are still some
manual steps required.  I have checked in a minimal `.idea` directory, so at
least all developers can share a single inspection profile, etc.

### Prerequisites

Before going any further, make sure sure that you installed all of the system
prerequisites discussed above.  Then, make sure your environment is in working
order.  In particular, if you do not run the install step, there will be no
virtualenv for IntelliJ to use:

```
$ run install
$ run test
$ run checks
```

Once you have a working shell development environment, **Open** (do not
**Import**) the `cedar-backup3` directory in IntelliJ and follow the remaining
instructions below.  (By using **Open**, the existing `.idea` directory will be
retained.)  

> _Note:_ If you get a **Frameworks Detected** message, ignore it for now,
> because IntelliJ might be trying to import some things which aren't really part
> of the project.

### Plugins

Install the following plugins:

|Plugin|Description|
|------|-----------|
|[Python](https://plugins.jetbrains.com/plugin/631-python)|Smart editing for Python code|

### Project and Module Setup

Run the following to find the location of the Python virtualenv managed by
Poetry:

```
$ poetry run which python
```

Right click on the `cedar-backup3` project in IntelliJ's project explorer and
choose **Open Module Settings**.  

Click on **Project**.  In the **Project SDK**, select the Python interpreter
virtualenv from above.  Then, under **Project compiler output**, enter `out`.  Then
click **Apply**.

Click on **Modules**.  On the **Sources** tab, find the `src` folder. Right
click on it and make sure the **Sources** entry is checked.  Without this,
IntelliJ sometimes does not recognize the source tree when trying to run
tests.

Still on the **Sources** tab, find the **Exclude files** box.  Enter the
following, and click **Apply**:

```
.coverage;.coveragerc;.github;.htmlcov;.idea;.isort.cfg;.pre-commit-config.yaml;.pylintrc;.pytest_cache;.readthedocs.yml;.tox;.toxrc;build;dist;docs/_build;out;poetry.lock;run
```

On the **Dependencies** tab, select the Python SDK you configured above as the
**Module SDK**, and click **OK**.

You should get a **Frameworks Detected** message again at this point.  If so,
click the **Configure** link and accept the defaults.

Finally, go to the gear icon in the project panel, and uncheck **Show Excluded
Files**.  This will hide the files and directories that were excluded above in
module configuration.

### Preferences

API documentation is written 
using [Google Style Python Docstring](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).  
However, this is not the default in IntelliJ.

Go to IntelliJ preferences, then select **Tools > Python Integrated Tools**.
Under **Docstrings > Docstring format**, select _Google_. Click **OK**.

### Running Unit Tests

Use **Build > Rebuild Project**, just to be sure that everything is up-to-date.
Then, right click on the `tests` folder in IntelliJ's project explorer and
choose **Run 'Unittests in tests'**.  Make sure that all of the tests pass.

### External Tools

Optionally, you might want to set up external tools in IntelliJ for some of
common developer tasks: code reformatting and the PyLint checks.  One nice
advantage of doing this is that you can configure an output filter, which makes
the Pylint errors clickable in IntelliJ.  To set up external tools, go to
IntelliJ preferences and find **Tools > External Tools**.  Add the tools as
described below.

#### Format Code

|Field|Value|
|-----|-----|
|Name|`Format Code`|
|Description|`Run the code formatters`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`format`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Checked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Unchecked_|
|Make console active on message in stderr|_Unchecked_|
|Output filters|_Empty_|

#### Run Pylint Checks

|Field|Value|
|-----|-----|
|Name|`Run Pylint Checks`|
|Description|`Run the Pylint code checks`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`pylint`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$:$COLUMN.*`|

## Release Process

### Documentation

Documentation at [Read the Docs](https://cedar-backup3.readthedocs.io/en/latest/)
is generated via a GitHub hook each time code is pushed to master.  So, there
is no formal release process for the documentation.

### Code

Code is released to [PyPI](https://pypi.org/project/cedar-backup3/).  There is a
manual process to publish a new release. 

Before publishing code, you must must have push permissions to the GitHub repo
and be a collaborator on the PyPI project.

First, configure an API token which has permission to publish to the
PyPI project.  This is a one-time step. In your PyPI [account settings](https://pypi.org/manage/account/),
create an API token with upload permissions.  Save off the token, and then tell
Poetry to use it, following the [instructions](https://python-poetry.org/docs/repositories/#configuring-credentials):

```
poetry config pypi-token.pypi my-token
```

To publish a new release, first ensure that you are on the `master` branch.
Releases must always be done from master.

Next, ensure that the `Changelog` is up-to-date and reflects all of the changes
that will be published.  The top line must show your version as unreleased:

```
Version 3.3.0     unreleased
```

Next, run the release step:

```
$ run release 3.3.0
```

This updates `pyproject.toml`, the `Changelog`, and `release.py` to reflect the
released version, then commits those changes and tags the code.  Nothing has
been pushed or published yet, so you can always remove the tag (i.e. `git tag
-d CEDAR_BACKUPV3_V3.3.0`) and revert your commit (`git reset HEAD~1`) if you
made a mistake.

Finally, publish the code:

```
$ run publish
```

This builds the deployment artifacts, publishes the artifacts to PyPI, and
pushes the repo to GitHub.  

The code will be available on PyPI for others to use after a little while,
sometimes within a minute or two, and sometimes as much as half an hour later.
