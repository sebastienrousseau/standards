Name:           standards-sync
Version:        @VERSION@
Release:        1%{?dist}
Summary:        Keep the code standards in sync without losing edits
License:        Apache-2.0 OR MIT
URL:            https://github.com/sebastienrousseau/standards
Source0:        @URL@
BuildArch:      noarch
Requires:       python3 >= 3.9
Requires:       git

%description
standards-sync copies five canonical standards files to the workspace
root and the dotfiles copies, keeps any copy edited in place instead of
overwriting it, and reports the drift with diffs.

%prep
%setup -q -n standards-sync-%{version}

%build

%install
mkdir -p %{buildroot}%{_prefix}
cp -a bin share %{buildroot}%{_prefix}/
rm -rf %{buildroot}%{_datadir}/licenses

%files
%license share/licenses/standards-sync/LICENSE-APACHE share/licenses/standards-sync/LICENSE-MIT
%{_bindir}/standards-sync
%{_mandir}/man1/standards-sync.1*
%{_datadir}/bash-completion/completions/standards-sync
%{_datadir}/zsh/site-functions/_standards-sync
%{_datadir}/fish/vendor_completions.d/standards-sync.fish
