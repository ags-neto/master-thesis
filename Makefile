# Makefile for the master-thesis LaTeX collection.  See README.md.
#
#   make test         compile and check every main document (slow, ~4 min)
#   make test-static  source checks only, no compilation (fast)
#   make build        compile every main document into build/ (not committed)
#   make clean        remove build/

SHELL := /bin/bash
DOCS := thesis papers/ibpria2025 papers/ibpria-extended2025 papers/demographic-bias papers/on-paper-data-aug
BUILD := build

.PHONY: all test test-static build clean help

all: help

help:
	@echo "make test         compile and check every main document"
	@echo "make test-static  source checks only (figures, citations)"
	@echo "make build        compile into $(BUILD)/ (not committed)"
	@echo "make clean        remove $(BUILD)/"

test:
	@tests/run.sh full

test-static:
	@tests/run.sh static

build:
	@mkdir -p $(BUILD)
	@for d in $(DOCS); do \
	  echo "== $$d"; \
	  mkdir -p "$(BUILD)/$$d"; \
	  ( cd "$$d" && latexmk -pdf -interaction=nonstopmode -file-line-error -outdir="$(CURDIR)/$(BUILD)/$$d" main.tex ) \
	    | tail -3; \
	done
	@echo "PDFs in $(BUILD)/<document>/main.pdf"

clean:
	@rm -rf $(BUILD)
	@echo "removed $(BUILD)/"
