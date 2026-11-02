Name:           claude-code-repo
Version:        1
Release:        0
Summary:        Anthropic's official Claude Code repository for Zypper
License:        GPL-3.0-or-later
URL:            https://github.com/lyra-os-linux/claude-code
Source0:        claude-code.repo
Source1:        claude-code.asc
Source2:        lyra-update-channel.json
BuildArch:      noarch
BuildRequires:  gpg2

%description
Registers Anthropic's official Claude Code Zypper repository
(downloads.claude.ai/claude-code/rpm/stable) together with the Claude Code release signing
key (31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE). The key is pinned
in this package because the repository does not publish repomd.xml.key; the
user still approves it the first time, in Vega or in Zypper. This package
carries no Claude Code binary: it only makes `zypper install claude-code` resolve
against Anthropic's own repository. It also sets Claude Code's update
channel to `stable`, the channel this repository publishes, so the CLI no
longer reports `latest` releases that Zypper cannot install yet.

%prep

%build

%install
install -D -m 0644 %{SOURCE0} %{buildroot}%{_sysconfdir}/zypp/repos.d/claude-code.repo
install -D -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/claude-code-repo/claude-code.asc
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/claude-code/managed-settings.d/lyra-update-channel.json

%check
repo=%{buildroot}%{_sysconfdir}/zypp/repos.d/claude-code.repo
grep -qxF 'baseurl=https://downloads.claude.ai/claude-code/rpm/stable' "$repo"
grep -qxF 'gpgkey=file://%{_datadir}/claude-code-repo/claude-code.asc' "$repo"
grep -qxF 'gpgcheck=1' "$repo"
grep -qxF 'repo_gpgcheck=1' "$repo"
grep -qxF 'priority=90' "$repo"
# The shipped key must be exactly the Claude Code release signing key.
export GNUPGHOME=$(mktemp -d)
fingerprints=$(gpg --batch --show-keys --with-colons %{buildroot}%{_datadir}/claude-code-repo/claude-code.asc | awk -F: '/^pub/{p=1;next} /^fpr/ && p {print $10; p=0}')
rm -rf "$GNUPGHOME"
test "$fingerprints" = "31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE"
# Claude Code must follow the channel this repository publishes.
grep -qF '"autoUpdatesChannel": "stable"' %{buildroot}%{_sysconfdir}/claude-code/managed-settings.d/lyra-update-channel.json

%files
%dir %{_sysconfdir}/zypp
%dir %{_sysconfdir}/zypp/repos.d
%config(noreplace) %{_sysconfdir}/zypp/repos.d/claude-code.repo
%dir %{_datadir}/claude-code-repo
%{_datadir}/claude-code-repo/claude-code.asc
%dir %{_sysconfdir}/claude-code
%dir %{_sysconfdir}/claude-code/managed-settings.d
%config(noreplace) %{_sysconfdir}/claude-code/managed-settings.d/lyra-update-channel.json

%changelog
