# -*- mode: GNUMakefile -*-
# g$Id$

# This Makefile is a simple "driver" script to automate tasks a
# platform developer would do in her sandbox all the time. Please
# read the comments.

.PHONY: info help tests testfailed pycoverage coverage preflight
	egg upload pycheck check pylint lint clean

TESTS = .
PY_FILE_DIRS = .

NOSE = nosetests
NOSEOPTS = -v --exe --with-id
NOSECOVOPTS = --with-coverage --cover-erase --cover-html --cover-package=benchmarktool
PYLINT = pylint
PYLINTOPTS = --rcfile=.pylintrc -E
PYCHECKER = flake8
PYCHECKEROPTS = --max-line-length=110

# Gather all Python files that have changed from the working set
PY_FILES := $(subst \,/,$(shell git status $(PY_FILE_DIRS) -s |\
	python -c 'import sys;\
	print " ".join([line[3:].strip() for line in sys.stdin.readlines() \
	if line.endswith(".py\n") and line[1] in ("AM")])'))

##
## This Makefile automates a lot of things you should do quite often in your
## sandbox, like running tests, code checkers etc. You can use this Makefile
## from anywhere in your tree like so:
##
##     $ make -C <sandbox> <target>
##
## The targets are explained below.

# Default target 'info': generate documentation by parsing all input
# files to GNU Make. Documentation lines are prefixed by '##'. The
# documentation is separated into sections. Section markers are lines
# starting with '## #'. Each file can contribute to each section. The
# unnamed "main" section is marked up by using '## #', and its content
# is printed first. For further details look at the python script.
info:
	@grep '^##' Makefile | sed -e 's/##//'

help: info

dist/.build: benchmarktool setup.py MANIFEST.in README.rst
	python setup.py bdist_egg
	touch dist/.build
egg: dist/.build

upload: egg
ifeq ($(ARMED),True)
	devpi login wen
	devpi upload --index apps/15.3 dist/benchmarktool-0.1-py2.7.egg
else
	# TODO: remove this temp. hack after the code base has been refactored
	rm -rf /home/wen/src/performance_testing/generate_series/benchmarktool-0.1-py2.7.egg/*
	unzip dist/benchmarktool-0.1-py2.7.egg -d /home/wen/src/performance_testing/generate_series/benchmarktool-0.1-py2.7.egg
	# devpi upload --index apps/15.3 --dry-run dist/benchmarktool-0.1-py2.7.egg
endif

clean:
	git clean -fd

##
## tests        Run all Python unit tests using 'nosetests'.
##              Tests are run using '--with-id', so that the
##              'testfailed' target can be used to repeat only the failing
##              ones. You can choose the set of tests by setting TESTS from
##              the make command line, using nose's test selection syntax,
##              for example:
##
##              make tests TESTS=benchmarktool/test/test_bla.py
tests:
	rm -f .noseids
	$(NOSE) $(NOSEOPTS) $(TESTS)

##
## testfailed   Re-run the failed unit tests. This is useful to save time while
##              implementing something. Uses nose's Testid plugin, see
##              http://nose.readthedocs.org/en/latest/plugins/testid.html
testfailed:
	$(NOSE) $(NOSEOPTS) --failed $(TESTS)

##
## coverage     Run nose coverage and generate reports
pycoverage:
	COVERAGE_OPTS='-m coverage run' $(NOSE) $(NOSECOVOPTS) $(NOSEOPTS) $(TESTS)

coverage: pycoverage

##
## preflight     Run basic pre-commit checks and tests, by doing 'tests' and
##               'pycheck'. Preflight currently does not run 'pylint'.
##
##                          >> DO THIS BEFORE COMMITTING <<
##                          >>  or baby seals will die!  <<
##
preflight:
	$(MAKE) tests
	-$(MAKE) pycheck

##
##
## # PYTHON CODE ANALYSIS

##
## The analysis targets check locally modified or added files
## only. The set of files is computed using 'svn status'.

##
## pycheck      Run $(PYCHECKER) on changes in the sandbox. Currently
##              PYCHECKER is flake8, which is part of the latest SDK.
##              'check' is an alias for 'pycheck'
.IGNORE: pycheck
pycheck:
ifneq ($(PY_FILES),)
	"$(PYCHECKER)" $(PYCHECKEROPTS) $(PY_FILES)
else
	@echo "pycheck: no modified Python files"
endif

check: pycheck

##
## pylint       Run pylint on changes in the sandbox.
pylint:
ifneq ($(PY_FILES),)
	"$(PYLINT)" $(PYLINTOPTS) $(PY_FILES)
else
	@echo "pylint: no modified Python files"
endif

lint: pylint

##
## # BEST PRACTICES

## * A failing test *always* is a bug. Fix the bug or fix the test!
##
## * All ERROR log messages appearing during a test run are bugs, too!
##   If the message is intentionally produced by the test, use
##   cdb.testcase.without_error_logging, etc. to suppress it. Otherwise
##   it's either a bug in the test case or in the product that must be
##   fixed.
##
## * Frequently run tests while implementing stuff, or even better,
##   implement tests *first*, watch them fail, and start doing the
##   implementation.  To restrict the set of tests to what you need,
##   use TESTS in the command line.
##
## * BEFORE committing anything "make preflight" and fix the issues.
##
## * Don't try to fix all style, PEP8 and linting issues in the code
##   surrounding your change -- lots of hunks unrelated to to your
##   intended change will confuse reviewers and future devs looking at
##   the history.
##
##   Collect hero points by fixing style/linting issues in a separate
##   change!
##
## * When there is a failing test induced by someone else's check-in, notify
##   that developer and ask them to fix the bug (or help them doing so).
##
