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


############################
# Locations and definitions
############################

AWK               = awk
CD                = cd
CP                = cp
ECHO              = echo
FIND              = find
MKDIR             = mkdir
MV                = mv
RM                = rm
SED               = sed
SUDO              = sudo
SETUPSSH          = $(HOME)/util/setupssh
TAR               = tar
VALIDATE          = util/validate

VIRTUALENV        = util/virtualenv
PYTHON_INSTALL    = .python
PYTHON_VERSION    = 3.5
PYTHON            = $(PYTHON_INSTALL)/bin/python
PYLINT            = $(PYTHON_INSTALL)/bin/pylint
COVERAGE          = $(PYTHON_INSTALL)/bin/coverage
SETUP             = $(PYTHON) setup.py

PACKAGE           = CedarBackup3
PACKAGE_LC        = cedar-backup3
VERSION           = `cat $(PACKAGE)/release.py | grep '^VERSION' | awk -F\" '{print $$2}'`
URL               = `cat $(PACKAGE)/release.py | grep URL | awk -F\" '{print $$2}'`

DOC_DIR           = doc
BITBUCKET_DIR     = ../gwt/CedarCommon/BitBucketSite
DIST_DIR          = build
MANUAL_SRC        = manual
SPHINX_SRC        = sphinx
SDIST_DIR         = $(DIST_DIR)/sdist
INTERFACE_DIR     = $(DOC_DIR)/interface
SPHINX_BUILD      = $(SPHINX_SRC)/_build
MANUAL_DIR        = $(DOC_DIR)/manual
CHANGELOG_FILE    = Changelog
COVERAGE_FILE     = .coverage
COVERAGE_DIR      = htmlcov


###################
# High-level rules
###################

all: 

tags:
	ctags `find . -name "*.py"`

clean: docclean distribclean coverageclean
	-@$(FIND) . -name "*.pyc" | xargs rm -f
	-@rm -f PKG-INFO tags 

distclean: clean virtualenvclean

virtualenv: 
	@$(VIRTUALENV) $(PYTHON_VERSION) $(PYTHON_INSTALL)

virtualenvclean:
	@rm -rf $(PYTHON_INSTALL)

# This uses the "full" argument to get all tests
# We prompt for passphrases and passwords up-front, to simplify things
test: virtualenv
	@$(SUDO) -v
	@$(SETUPSSH)
	@$(PYTHON) util/test.py full

# This leaves off "full" and gets on the tests most end-users would run
usertest: virtualenv
	@$(PYTHON) util/test.py

# This gets coverage for the full tests
coverage: virtualenv
	@$(SUDO) -v
	@$(COVERAGE) run --source=$(PACKAGE) util/test.py full
	@$(COVERAGE) html
	@echo "Coverage at: file://$(PWD)/$(COVERAGE_DIR)/index.html"

# This gets coverage for the user tests
usercoverage: virtualenv
	@$(COVERAGE) run --source=$(PACKAGE) util/test.py
	@$(COVERAGE) html
	@echo "Coverage at: file://$(PWD)/$(COVERAGE_DIR)/index.html"

coverageclean:
	@rm -f $(COVERAGE_FILE)
	@rm -rf $(COVERAGE_DIR)


##################################
# Stylistic and function checking
##################################

check: virtualenv
	-@$(PYLINT) --rcfile=pylint-code.rc $(PACKAGE) cback3 util setup.py

testcheck: virtualenv
	-@$(PYLINT) --rcfile=pylint-test.rc testcase

# Trim trailing whitespace from lines in source files
trim:
	-@$(FIND) . -name "*.py" -exec $(SED) -i 's/\s*$$//g' \{} \;


################
# Documentation
################

# Aliases, since I can't remember what to type. :)
docs: doc
docsclean: docclean
interface: interface-doc
book: manual

doc: interface-doc manual-doc

interface-doc: interface-html 

interface-html: $(INTERFACE_DIR)
	@rm -rf $(INTERFACE_DIR)/*
	@rm -rf $(SPHINX_BUILD)/*
	@$(CD) $(SPHINX_SRC) && $(MAKE) html 
	@cp -r $(SPHINX_BUILD)/html/* $(INTERFACE_DIR)

manual-doc: $(MANUAL_DIR)
	@$(CD) $(MANUAL_SRC) && $(MAKE) install

# For convenience, this rule builds chunk only
manual: 
	-@$(CD) $(MANUAL_SRC) && $(MAKE) manual-chunk && $(MAKE) install-manual-chunk

validate: 
	-@$(VALIDATE) $(MANUAL_SRC)/src/book.xml

docclean:
	-@$(CD) $(MANUAL_SRC) && $(MAKE) clean
	-@$(CD) $(SPHINX_SRC) && $(MAKE) clean
	-@$(RM) -rf $(INTERFACE_DIR)
	-@$(RM) -rf $(MANUAL_DIR)

$(MANUAL_DIR):
	@$(MKDIR) -p $(MANUAL_DIR)

$(INTERFACE_DIR):
	@$(MKDIR) -p $(INTERFACE_DIR)


################
# Distributions
################
# The rules in this section build a Python source distribution, and then
# also that same source distribution named appropriately for Debian (the
# Debian packages are maintained via svn-buildpackage as usual).  This
# keeps cedar-backup3 from being a Debian-native package.

distrib: debdist

distribclean: sdistclean debdistclean
	-@$(RM) -f MANIFEST 
	-@$(RM) -rf $(DIST_DIR)

sdist: virtualenv $(SDIST_DIR) doc
	@$(SETUP) sdist --dist-dir $(SDIST_DIR)
	@$(CP) $(SDIST_DIR)/$(PACKAGE)-$(VERSION).tar.gz ../

source: virtualenv $(SDIST_DIR) 
	@$(SETUP) sdist --dist-dir $(SDIST_DIR)
	@$(CP) $(SDIST_DIR)/$(PACKAGE)-$(VERSION).tar.gz ../

$(SDIST_DIR):
	@$(MKDIR) -p $(SDIST_DIR)

sdistclean: 
	@$(RM) -f $(SDIST_DIR)/$(PACKAGE)-$(VERSION).tar.gz

debdist: sdist
	@$(CP) $(SDIST_DIR)/$(PACKAGE)-$(VERSION).tar.gz $(SDIST_DIR)/$(PACKAGE_LC)_$(VERSION).orig.tar.gz
	@$(CP) $(SDIST_DIR)/$(PACKAGE_LC)_$(VERSION).orig.tar.gz ../

debdistclean: 
	@$(RM) -f $(SDIST_DIR)/$(PACKAGE_LC)_$(VERSION).orig.tar.gz 

# This layout matches the htdocs/docs tree for the website
htmldoc: htmldocs
htmldocs: docdist
docdist: doc
	@$(MKDIR) -p $(BITBUCKET_DIR)/docs/$(PACKAGE_LC)/
	@$(CP) $(CHANGELOG_FILE) $(BITBUCKET_DIR)/docs/$(PACKAGE_LC)/
	@$(CP) -r $(MANUAL_DIR) $(BITBUCKET_DIR)/docs/$(PACKAGE_LC)/
	@$(CP) -r $(INTERFACE_DIR) $(BITBUCKET_DIR)/docs/$(PACKAGE_LC)/


##################################
# Phony rules for use by GNU make
##################################

.PHONY: all clean tags test usertest check testcheck doc docs docclean docsclean interface interface-doc interface-html book validate manual manual-doc distrib distribclean sdist sdistclean debdist debdistclean docdist virtualenv virtualenvclean coverage coverageclean

