# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Developer tasks. `make check` is the single gate: it runs every check CI
# runs except the external link check (make linkcheck, which needs the
# network and lychee). The install contract lives in GNUmakefile.

UV       ?= uv
RUN      := $(UV) run --frozen
NPX      ?= npx --yes
MDLINT   := markdownlint-cli2@0.24.1
VERSION  := $(shell sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml)
BUILD    := build
SHELLS   := bash zsh fish

.PHONY: help check lint fmt test fuzz docs linkcheck api audit man completions \
        templates dist reproducible sbom demo clean

help: ## List the tasks
	@grep -hE '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

check: lint test fuzz docs api audit reproducible ## Run every gate CI runs
	@echo "make check: all gates passed"

lint: ## Lint and format checks, complexity, spelling, Markdown, REUSE, workflows, docs
	$(RUN) ruff check .
	$(RUN) ruff format --check .
	$(RUN) python scripts/check_complexity.py
	$(RUN) python scripts/check_docs.py
	$(RUN) codespell
	$(RUN) reuse lint --quiet
	$(NPX) $(MDLINT)
	actionlint
	@! grep -n "—" README.md PR-TEMPLATE.md CHANGELOG.md || { echo "em dash found"; exit 1; }

fmt: ## Format the Python sources
	$(RUN) ruff check --fix .
	$(RUN) ruff format .

test: ## Unit tests with the coverage gate
	$(RUN) coverage run -m pytest tests
	$(RUN) coverage report

fuzz: ## Property-based fuzzing with the regression corpus
	$(RUN) pytest fuzz

docs: ## Build the manual with warnings as errors, then check every page
	$(RUN) zensical build --strict --clean
	rm -rf $(BUILD)/site && mkdir -p $(BUILD) && mv site $(BUILD)/site
	$(RUN) python scripts/check_docs.py --site $(BUILD)/site

linkcheck: docs ## Check every link in the docs and the built manual (network)
	lychee --no-progress --exclude-path $(BUILD)/site/404.html '*.md' 'docs/**/*.md' '$(BUILD)/site/**/*.html'

api: ## Fail on a breaking change to sync.py's public API since the last release
	$(RUN) python scripts/check_api.py

audit: ## Advisory audit of every locked dependency, by hash
	@mkdir -p $(BUILD)
	$(UV) export --frozen --no-emit-project --format requirements.txt --output-file $(BUILD)/requirements.txt
	$(RUN) pip-audit --strict --disable-pip --require-hashes -r $(BUILD)/requirements.txt

man: ## Generate the manpage from the argument parser
	@mkdir -p $(BUILD)/man
	$(RUN) argparse-manpage --pyfile scripts/sync.py --function build_parser --prog standards-sync \
	  --project-name standards --version $(VERSION) --author "Sebastien Rousseau" \
	  --manual-title "standards-sync manual" --description "keep the code standards in sync" \
	  --url https://github.com/sebastienrousseau/standards --output $(BUILD)/man/standards-sync.1

completions: ## Generate bash, zsh and fish completions from the argument parser
	@mkdir -p $(BUILD)/completions
	@for sh in $(SHELLS); do \
	  PYTHONPATH=scripts $(RUN) shtab --shell=$$sh --prog standards-sync sync.build_parser \
	    > $(BUILD)/completions/standards-sync.$$sh || exit 1; \
	done

templates: ## Copy the canonical PR template to where GitHub reads it
	cp PR-TEMPLATE.md .github/pull_request_template.md

dist: ## Build the wheel and sdist
	$(UV) build --out-dir dist

reproducible: ## Build twice and require byte-identical artifacts
	rm -rf $(BUILD)/repro-a $(BUILD)/repro-b
	SOURCE_DATE_EPOCH=$$(git log -1 --format=%ct) $(UV) build -q --out-dir $(BUILD)/repro-a
	SOURCE_DATE_EPOCH=$$(git log -1 --format=%ct) $(UV) build -q --out-dir $(BUILD)/repro-b
	cd $(BUILD)/repro-a && shasum -a 256 * > ../repro-a.sha256
	cd $(BUILD)/repro-b && shasum -a 256 * > ../repro-b.sha256
	diff $(BUILD)/repro-a.sha256 $(BUILD)/repro-b.sha256
	@echo "reproducible: both builds byte-identical"

sbom: ## CycloneDX SBOM of the locked dependency tree
	@mkdir -p $(BUILD)
	$(UV) export --frozen --format cyclonedx1.5 --output-file $(BUILD)/standards-sync.cdx.json

demo: ## Re-render .github/demo.gif from .github/demo.tape (needs vhs)
	vhs .github/demo.tape

clean: ## Remove build output
	rm -rf $(BUILD) dist site .coverage .pytest_cache .hypothesis .ruff_cache
