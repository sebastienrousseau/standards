# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# The README demo: make demo renders .github/demo.gif from this file.
# It runs the real standards-sync from this checkout against a scratch
# target directory, so it touches nothing outside build/.

Output .github/demo.gif
Require python3

Set Shell "bash"
Set FontSize 15
Set Width 1280
Set Height 640
Set Padding 20
Set TypingSpeed 35ms
Set Theme "Catppuccin Mocha"

Hide
Type "rm -rf build/demo && mkdir -p build/demo && export STANDARDS_REPO=$PWD STANDARDS_TARGETS=$PWD/build/demo PS1='$ ' && alias standards-sync='python3 scripts/sync.py' && clear"
Enter
Show

Type "standards-sync --push"
Enter
Sleep 2s

Type "echo 'a local edit' >> build/demo/AGENTS.md"
Enter
Sleep 500ms

Type "standards-sync --push | grep -v COPIED"
Enter
Sleep 3s

Type "standards-sync --check | grep -E 'DRIFTED|^[-+]|failed'"
Enter
Sleep 4s
