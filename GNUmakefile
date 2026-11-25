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

.PHONY: all install uninstall

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
