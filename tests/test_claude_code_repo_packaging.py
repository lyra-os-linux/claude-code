from __future__ import annotations

import configparser
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANTHROPIC = "31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE"


class ClaudeCodeRepoPackagingTests(unittest.TestCase):
    def test_repo_file_points_at_anthropic_official_repository(self) -> None:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ROOT / "claude-code.repo", encoding="utf-8")
        self.assertEqual(parser.sections(), ["claude-code"])
        repo = parser["claude-code"]
        self.assertEqual(repo["baseurl"], "https://downloads.claude.ai/claude-code/rpm/stable")
        self.assertEqual(repo["gpgcheck"], "1")
        self.assertEqual(repo["repo_gpgcheck"], "1")
        self.assertEqual(repo["gpgkey"], "file:///usr/share/claude-code-repo/claude-code.asc")
        self.assertEqual(repo["priority"], "90")

    def test_shipped_key_is_anthropic_signing_key(self) -> None:
        if not shutil.which("gpg"):
            self.skipTest("gpg não instalado")
        with tempfile.TemporaryDirectory() as home:
            out = subprocess.run(
                ["gpg", "--homedir", home, "--batch", "--show-keys", "--with-colons", str(ROOT / "claude-code.asc")],
                capture_output=True, text=True, check=True,
            ).stdout
        primary = []
        after_pub = False
        for line in out.splitlines():
            fields = line.split(":")
            if fields[0] == "pub":
                after_pub = True
            elif fields[0] == "fpr" and after_pub:
                primary.append(fields[9])
                after_pub = False
        self.assertEqual(primary, [ANTHROPIC])

    def test_update_channel_matches_repository_channel(self) -> None:
        settings = json.loads((ROOT / "lyra-update-channel.json").read_text(encoding="utf-8"))
        self.assertEqual(settings, {"autoUpdatesChannel": "stable"})
        spec = (ROOT / "claude-code-repo.spec").read_text(encoding="utf-8")
        self.assertIn("%{_sysconfdir}/claude-code/managed-settings.d/lyra-update-channel.json", spec)

    def test_package_ships_no_upstream_binary(self) -> None:
        spec = (ROOT / "claude-code-repo.spec").read_text(encoding="utf-8")
        self.assertNotIn("_service", [p.name for p in ROOT.iterdir()])
        self.assertIn("%config(noreplace)", spec)
        self.assertIn(ANTHROPIC, spec)

    def test_repo_file_install_and_removal_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "etc/zypp/repos.d/claude-code.repo"

            def install() -> None:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "claude-code.repo", destination)
                destination.chmod(0o644)

            def remove() -> None:
                destination.unlink(missing_ok=True)

            install()
            first = destination.read_bytes()
            install()
            self.assertEqual(destination.read_bytes(), first)
            self.assertEqual(destination.stat().st_mode & 0o777, 0o644)
            remove()
            remove()
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
