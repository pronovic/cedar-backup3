# vim: set ft=bash sw=3 ts=3 expandtab:

# The release process for Cedar Backup is a little different than the standard
# process, because it has a different set of files to update.  As a result, we
# can't rely on "run_command tagrelease" like usual.  This version is less 
# general than the standard version, since it won't be used anywhere else.

help_release() {
   echo "- run release: Release a specific version and tag the code"
}

task_release() {
   local VERSION COPYRIGHT DATE TAG FILES MESSAGE

   if [ $# != 1 ]; then
      echo "<version> required"
      exit 1
   fi

   VERSION=$(echo "$1" | sed 's/^v//') # so you can use "0.1.5 or "v0.1.5"
   COPYRIGHT="2004-$(date +'%Y')"
   DATE=$(date +'%d %b %Y')
   TAG="v$VERSION" # follow PEP 440 naming convention
   FILES="CREDITS pyproject.toml Changelog src/CedarBackup3/release.py"
   MESSAGE="Release v$VERSION to PyPI"

   if [ "$(git branch -a | grep '^\*' | sed 's/^\* //')" != "master" ]; then
      echo "*** You are not on master; you cannot release from this branch"
      exit 1
   fi

   git tag -l "$TAG" | grep -q "$TAG"
   if [ $? = 0 ]; then
      echo "*** Version v$VERSION already tagged"
      exit 1
   fi

   head -1 Changelog | grep -q "^Version $VERSION\s\s*unreleased"
   if [ $? != 0 ]; then
      echo "*** Unreleased version v$VERSION is not at the head of the Changelog"
      exit 1
   fi

   poetry version $VERSION
   if [ $? != 0 ]; then
      echo "*** Failed to update version"
      exit 1
   fi

   run_command dos2unix pyproject.toml

   # annoyingly, BSD sed and GNU sed are not compatible on the syntax for -i
   # I failed miserably in all attempts to put the sed command (with empty string) into a variable
   sed --version 2>&1 | grep -iq "GNU sed"
   if [ $? = 0 ]; then
      # GNU sed accepts a bare -i and assumes no backup file
      sed -i "s/^COPYRIGHT = .*$/COPYRIGHT = \"$COPYRIGHT\"/g" src/CedarBackup3/release.py
      sed -i "s/^VERSION = .*$/VERSION = \"$VERSION\"/g" src/CedarBackup3/release.py
      sed -i "s/^DATE = .*$/DATE = \"$DATE\"/g" src/CedarBackup3/release.py
      sed -i "s/^Version $VERSION\s\s*unreleased/Version $VERSION     $DATE/g" Changelog
      sed -i -E "s/(^ *Copyright \(c\) *)([0-9,-]+)( *Kenneth.*$)/\1$COPYRIGHT\3/" CREDITS
   else
      # BSD sed requires you to set an empty backup file extension
      sed -i "" "s/^COPYRIGHT = .*$/COPYRIGHT = \"$COPYRIGHT\"/g" src/CedarBackup3/release.py
      sed -i "" "s/^VERSION = .*$/VERSION = \"$VERSION\"/g" src/CedarBackup3/release.py
      sed -i "" "s/^DATE = .*$/DATE = \"$DATE\"/g" src/CedarBackup3/release.py
      sed -i "" "s/^Version $VERSION\s\s*unreleased/Version $VERSION     $DATE/g" Changelog
      sed -i "" -E "s/(^ *Copyright \(c\) *)([0-9,-]+)( *Kenneth.*$)/\1$COPYRIGHT\3/" CREDITS
   fi

   git diff $FILES

   git commit --no-verify -m "$MESSAGE" $FILES
   if [ $? != 0 ]; then
      echo "*** Commit step failed"
      exit 1
   fi

   git tag -a "$TAG" -m "$MESSAGE"
   if [ $? != 0 ]; then
      echo "*** Tag step failed"
      exit 1
   fi

   echo ""
   echo "*** Version v$VERSION has been released and commited; you may publish now"
   echo ""
}

