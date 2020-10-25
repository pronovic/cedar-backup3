# Release Procedure

These are my partially-obsolete notes about the release procedure that I
follow.  As I finalize the new procedure for PyPI, these will be updated.

- Make final update to Changelog
- Update CedarBackup3/release.py
- Check in changes 
- Run unit tests one last time (make test)
- Run pylint tests one last time (make check)
- Build the source distributions (make distrib)
- Remember that gh-pages has the docs, but there's no process yet to regenerate them (probably doesn't matter)
- Push to GitHub
- Tag the code at GitHub as CEDAR_BACKUP3_VX.Y.Z and attach the file release

- Copy the source package to hcoop and install it for my use (if desired)
- Copy the source package to the FTP directory on mars and then synchronize HCOOP

- Copy the orig file into the tarballs directory for stable and unstable
- Build the Debian package for unstable in a chroot
- Build the Debian package for stable in a chroot
- Stage the latest Debian packages to mars and then synchronize HCOOP
- Upload the new packages to the Debian servers
