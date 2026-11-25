# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# The Unix install contract for standards-sync. GNU make reads this file
# first; the developer tasks come from Makefile.
#
#   make install                      to /usr/local
#   make PREFIX=$HOME/.local install  per user
#   make DESTDIR=/tmp/stage install   staged, for packagers

include Makefile

PREFIX    ?= /usr/local
BINDIR    ?= $(PREFIX)/bin
MANDIR    ?= $(PREFIX)/share/man/man1
BASHCOMP  ?= $(PREFIX)/share/bash-completion/completions
ZSHCOMP   ?= $(PREFIX)/share/zsh/site-functions
FISHCOMP  ?= $(PREFIX)/share/fish/vendor_completions.d
INSTALL   ?= install

.PHONY: all install uninstall pkg

all: man completions ## Generate the manpage and completions

install: all ## Install standards-sync, its manpage and completions under DESTDIR/PREFIX
	$(INSTALL) -d $(DESTDIR)$(BINDIR) $(DESTDIR)$(MANDIR) $(DESTDIR)$(BASHCOMP) $(DESTDIR)$(ZSHCOMP) $(DESTDIR)$(FISHCOMP)
	$(INSTALL) -m 755 scripts/sync.py $(DESTDIR)$(BINDIR)/standards-sync
	$(INSTALL) -m 644 $(BUILD)/man/standards-sync.1 $(DESTDIR)$(MANDIR)/standards-sync.1
	$(INSTALL) -m 644 $(BUILD)/completions/standards-sync.bash $(DESTDIR)$(BASHCOMP)/standards-sync
	$(INSTALL) -m 644 $(BUILD)/completions/standards-sync.zsh $(DESTDIR)$(ZSHCOMP)/_standards-sync
	$(INSTALL) -m 644 $(BUILD)/completions/standards-sync.fish $(DESTDIR)$(FISHCOMP)/standards-sync.fish

uninstall: ## Remove what install put under DESTDIR/PREFIX
	rm -f $(DESTDIR)$(BINDIR)/standards-sync $(DESTDIR)$(MANDIR)/standards-sync.1 \
	  $(DESTDIR)$(BASHCOMP)/standards-sync $(DESTDIR)$(ZSHCOMP)/_standards-sync \
	  $(DESTDIR)$(FISHCOMP)/standards-sync.fish

# The distribution packages' inputs (scripts/pkg.py): the tree that install
# writes, with the licences, packed as standards-sync-<v>-unix.tar.gz, and
# the recipes in pkg/ rendered against it, in build/pkg.
PKG_STAGE := $(BUILD)/pkg/stage

pkg: DESTDIR = $(PKG_STAGE)
pkg: PREFIX = /standards-sync-$(VERSION)
pkg: clean-pkg install ## Package tarball, deb root, rpm spec, PKGBUILD, Homebrew formula, Nix expression
	$(INSTALL) -d $(PKG_STAGE)$(PREFIX)/share/licenses/standards-sync
	$(INSTALL) -m 644 LICENSE-APACHE LICENSE-MIT $(PKG_STAGE)$(PREFIX)/share/licenses/standards-sync/
	$(RUN) python scripts/pkg.py --stage $(PKG_STAGE) --out $(BUILD)/pkg $(if $(URL_BASE),--url-base $(URL_BASE))

.PHONY: clean-pkg
clean-pkg:
	rm -rf $(BUILD)/pkg
