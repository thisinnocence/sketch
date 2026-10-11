# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

ifeq ($(shell uname -s),Linux)
COLOR_RED    := $(shell printf '\033[1;31m')
COLOR_YELLOW := $(shell printf '\033[1;33m')
COLOR_RESET  := $(shell printf '\033[0m')

define VENV_HELP
$(COLOR_RED)Activate the project's uv virtual environment before running make:$(COLOR_RESET)
$(COLOR_YELLOW)  uv venv
  uv pip install --python .venv/bin/python -r requirements.txt
  source .venv/bin/activate
  make$(COLOR_RESET)
endef

ifneq ($(abspath $(VIRTUAL_ENV)),$(CURDIR)/.venv)
$(error $(VENV_HELP))
endif
ifeq ($(wildcard .venv/bin/sphinx-build),)
$(error $(COLOR_RED)Project Sphinx is missing.$(COLOR_RESET) $(COLOR_YELLOW)Run: uv pip install --python .venv/bin/python -r requirements.txt$(COLOR_RESET))
endif
override SPHINXBUILD := $(CURDIR)/.venv/bin/sphinx-build
endif

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.DEFAULT_GOAL := html

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
