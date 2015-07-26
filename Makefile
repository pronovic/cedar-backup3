# vim: set ft=make:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#              C E D A R
#          S O L U T I O N S       "Software done right."
#           S O F T W A R E
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Make
# Project  : Cedar Backup, release 3
# Purpose  : Developer "private" makefile for CedarBackup3 package
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########
# Notes
########

# This file is the one that I will use for my personal development
# effort.  It has a number of rules in it that no one else will use,
# and it will not be included in any of the public distributions of
# CedarBackup3.


########################
# Programs and commands
########################

CD                = cd
CP                = cp
MV                = mv
EPYDOC            = epydoc
FIND              = find
MKDIR             = mkdir
PYLINT            = pylint
PYTHON            = python3 
COVERAGE          = python3-coverage
RM                = rm
SETUP             = $(PYTHON) ./setup.py
SUDO              = sudo
TAR               = tar
VALIDATE          = util/validate
VERSION           = `cat CedarBackup3/release.py | grep '^VERSION' | awk -F\" '{print $$2}'`
URL               = `cat CedarBackup3/release.py | grep URL | awk -F\" '{print $$2}'`


############
# Locations
############

DOC_DIR           = doc
DIST_DIR          = build
MANUAL_SRC        = manual
SDIST_DIR         = $(DIST_DIR)/sdist
INTERFACE_DIR     = $(DOC_DIR)/interface
INTERFACE_TEMPDIR = $(DOC_DIR)/interface/tmp
MANUAL_DIR        = $(DOC_DIR)/manual


###################
# High-level rules
###################

all: 

clean: docclean distribclean 
	-@$(FIND) . -name "*.pyc" | xargs rm -f
	-@rm -f PKG-INFO tags

tags:
	ctags `find . -name "*.py"`

# This uses the "full" argument to get all tests
test:
	@$(SUDO) -v
	@$(PYTHON) util/test.py full

# This leaves off "full" and gets on the tests most end-users would run
usertest:
	@$(PYTHON) util/test.py

# This gets coverage for the full tests
coverage:
	@$(SUDO) -v
	@$(COVERAGE) run --source CedarBackup3 util/test.py full
	@$(COVERAGE) html
	@echo "Coverage at: file://${PWD}/htmlcov/index.html"

# This gets coverage for the user tests
usercoverage:
	@$(COVERAGE) run --source CedarBackup3 util/test.py
	@$(COVERAGE) html
	@echo "Coverage at: file://${PWD}/htmlcov/index.html"


##################################
# Stylistic and function checking
##################################
# Previously, I used pychecker.  However, it's getting a little long in the
# tooth, and it doesn't work as well with newer versions of Python.  I've
# switched to pylint, which seems a bit more reliable and can be configured at
# a finer-grained level.

check:
	-@$(PYLINT) --rcfile=pylint-code.rc CedarBackup3

allcheck:
	-@$(PYLINT) --rcfile=pylint-code.rc CedarBackup3 util setup.py
	-@$(PYLINT) --rcfile=pylint-test.rc testcase


################
# Documentation
################

# Aliases, since I can't remember what to type. :)
docs: doc
docsclean: docclean
epydoc: interface-html
interface: interface-doc
book: manual

doc: interface-doc manual-doc

interface-doc: interface-html 

interface-html: $(INTERFACE_DIR)
	@$(EPYDOC) -v --html --name "CedarBackup3" --output $(INTERFACE_DIR) --url $(URL) CedarBackup3/

manual-doc: $(MANUAL_DIR)
	@$(CD) $(MANUAL_SRC) && $(MAKE) install

# For convenience, this rule builds chunk only
manual: 
	-@$(CD) $(MANUAL_SRC) && $(MAKE) manual-chunk && $(MAKE) install-manual-chunk

validate: 
	-@$(VALIDATE) $(MANUAL_SRC)/src/book.xml

docclean:
	-@$(CD) $(MANUAL_SRC) && $(MAKE) clean
	-@$(RM) -rf $(INTERFACE_DIR)
	-@$(RM) -rf $(INTERFACE_TEMPDIR)
	-@$(RM) -rf $(MANUAL_DIR)

$(MANUAL_DIR):
	@$(MKDIR) -p $(MANUAL_DIR)

$(INTERFACE_DIR):
	@$(MKDIR) -p $(INTERFACE_DIR)

$(INTERFACE_TEMPDIR):
	@$(MKDIR) -p $(INTERFACE_TEMPDIR)


################
# Distributions
################
# The rules in this section build a Python source distribution, and then
# also that same source distribution named appropriately for Debian (the
# Debian packages are maintained via svn-buildpackage as usual).  This
# keeps cedar-backup3 from being a Debian-native package.

distrib: debdist docdist

distribclean: sdistclean debdistclean
	-@$(RM) -f MANIFEST 
	-@$(RM) -rf $(DIST_DIR)

sdist: $(SDIST_DIR) doc
	@$(SETUP) sdist --dist-dir $(SDIST_DIR)
	@$(CP) $(SDIST_DIR)/CedarBackup3-$(VERSION).tar.gz ../

source: $(SDIST_DIR) 
	@$(SETUP) sdist --dist-dir $(SDIST_DIR)
	@$(CP) $(SDIST_DIR)/CedarBackup3-$(VERSION).tar.gz ../

$(SDIST_DIR):
	@$(MKDIR) -p $(SDIST_DIR)

sdistclean: 
	@$(RM) -f $(SDIST_DIR)/CedarBackup3-$(VERSION).tar.gz

debdist: sdist
	@$(CP) $(SDIST_DIR)/CedarBackup3-$(VERSION).tar.gz $(SDIST_DIR)/cedar-backup3_$(VERSION).orig.tar.gz
	@$(CP) $(SDIST_DIR)/cedar-backup3_$(VERSION).orig.tar.gz ../

debdistclean: 
	@$(RM) -f $(SDIST_DIR)/cedar-backup3_$(VERSION).orig.tar.gz 

# This layout matches the htdocs/docs tree for the website
htmldocs: docdist
docdist: doc
	@$(MKDIR) -p $(DOC_DIR)/tmp/docs/cedar-backup3/
	@$(MKDIR) -p $(DOC_DIR)/tmp/docs/cedar-backup3/
	@$(CP) Changelog $(DOC_DIR)/tmp/docs/cedar-backup3/
	@$(CP) -r $(MANUAL_DIR) $(DOC_DIR)/tmp/docs/cedar-backup3/
	@$(CP) -r $(INTERFACE_DIR) $(DOC_DIR)/tmp/docs/cedar-backup3/
	@$(CD) $(DOC_DIR)/tmp && $(TAR) -zcvf ../htmldocs.tar.gz docs/
	@$(MV) $(DOC_DIR)/htmldocs.tar.gz ../
	@$(RM) -rf $(DOC_DIR)/tmp


##################################
# Phony rules for use by GNU make
##################################

.PHONY: all clean tags test usertest check allcheck doc docs docclean docsclean epydoc interface interface-doc interface-html book validate manual manual-doc distrib distribclean sdist sdistclean debdist debdistclean docdist

