"""Observable packaging, provenance, and safe-install behavior."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("package_lapdex", ROOT / "scripts" / "package_lapdex.py")
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lapdex-package-test-")
        self.temp = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def build(self):
        return package.build_archive(self.temp / "dist")

    def rewrite(self, original, replacements=None, extra=()):
        rewritten = self.temp / "changed.zip"
        replacements = replacements or {}
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(rewritten, "w") as target:
            for info in source.infolist():
                target.writestr(info, replacements.get(info.filename, source.read(info)))
            for name, data in extra:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    target.writestr(name, data)
        return rewritten

    def test_build_and_install_from_unrelated_working_directory(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "package_lapdex.py"),
             "--output", str(self.temp / "dist")], cwd=self.temp,
            capture_output=True, text=True, check=True,
        )
        self.assertIn("Built:", result.stdout)
        archive = self.temp / "dist" / package.ARCHIVE_NAME
        manifest, payload = package.read_archive(archive)
        self.assertEqual(manifest["name"], "laco-laoshifu")
        self.assertNotIn("docs", {Path(name).parts[0] for name in payload})
        self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in payload))
        # Lapdex prunes references/ while scanning: only this entry is discovered.
        self.assertEqual([name for name in payload if name.endswith("SKILL.md")
                          and not name.startswith("references/")], ["SKILL.md"])
        checksum_line = archive.with_name(archive.name + ".sha256").read_text(encoding="ascii")
        self.assertEqual(checksum_line.split()[0], package.sha256(archive.read_bytes()))
        skills_dir = self.temp / "install" / "skills"
        planned = package.install_archive(archive, skills_dir, dry_run=True)
        self.assertFalse(skills_dir.exists())
        installed = package.install_archive(archive, skills_dir)
        self.assertEqual(planned, installed)
        for relative, data in payload.items():
            self.assertEqual((installed / relative).read_bytes(), data)
        # The installed KB must locate its own resources, independently of cwd.
        query = subprocess.run(
            [sys.executable, "-B", str(installed / package.RESOURCE_ROOT / "source" / "tools" / "kb.py"),
             "abbr", "硼扩散", "--json"], cwd=self.temp,
            capture_output=True, encoding="utf-8", check=True,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        self.assertIn("硼扩", query.stdout)
        self.assertIn("BK", query.stdout)
        subprocess.run(
            [sys.executable, "-B", str(installed / package.RESOURCE_ROOT / "source" / "tools" / "kb.py"),
             "verify"], cwd=self.temp, capture_output=True, encoding="utf-8", check=True,
            env={**os.environ, "PYTHONUTF8": "1"},
        )

    def test_all_sixteen_original_snapshots_keep_exact_bytes(self):
        archive = self.build()
        _, payload = package.read_archive(archive)
        original = json.loads((ROOT / "source" / "manifest.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(len(original["files"]), 16)
        for record in original["files"]:
            name = f"{package.RESOURCE_ROOT}/source/" + record["path"]
            self.assertEqual(payload[name], (ROOT / "source" / record["path"]).read_bytes())
            self.assertEqual(package.sha256(payload[name]), record["sha256"])

    def test_existing_build_and_install_are_preserved(self):
        archive = self.build()
        original = archive.read_bytes()
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(archive.read_bytes(), original)
        self.assertEqual(package.build_archive(self.temp / "dist", force=True), archive)
        installed = package.install_archive(archive, self.temp / "skills")
        user_file = installed / "local-notes.txt"
        user_file.write_text("retain", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            package.install_archive(archive, self.temp / "skills")
        self.assertEqual(user_file.read_text(encoding="utf-8"), "retain")

    def test_output_cannot_be_written_inside_packaged_resource_trees(self):
        for name in ("source", "skills"):
            with self.subTest(directory=name), self.assertRaises(ValueError):
                package.build_archive(ROOT / name / "build-output")

    def test_corrupt_payload_and_unlisted_file_are_rejected(self):
        archive = self.build()
        changed = self.rewrite(archive, {
            f"laco-laoshifu/{package.RESOURCE_ROOT}/source/README.md": b"changed"})
        with self.assertRaisesRegex(ValueError, "checksum"):
            package.read_archive(changed)
        changed = self.rewrite(archive, extra=[("laco-laoshifu/unlisted.txt", b"extra")])
        with self.assertRaisesRegex(ValueError, "every payload"):
            package.read_archive(changed)

    def test_path_traversal_duplicates_case_collisions_and_links_are_rejected(self):
        archive = self.build()
        for name in ("laco-laoshifu/../escape", "/absolute", "laco-laoshifu/C:/escape",
                     "laco-laoshifu\\escape", "laco-laoshifu/SKILL.md", "laco-laoshifu/skill.md"):
            with self.subTest(name=name):
                changed = self.rewrite(archive, extra=[(name, b"extra")])
                with self.assertRaises(ValueError):
                    package.read_archive(changed)
        linked = zipfile.ZipInfo("laco-laoshifu/link")
        linked.create_system = 3
        linked.external_attr = (stat.S_IFLNK | 0o777) << 16
        changed = self.rewrite(archive, extra=[(linked, b"../outside")])
        with self.assertRaisesRegex(ValueError, "links"):
            package.read_archive(changed)

    def test_original_snapshot_cannot_be_changed_by_rewriting_bundle_manifest(self):
        archive = self.build()
        manifest, payload = package.read_archive(archive)
        name = next(name for name in payload
                    if name.startswith(f"{package.RESOURCE_ROOT}/source/references/kd/"))
        modified = b"replaced original"
        for record in manifest["files"]:
            if record["path"] == name:
                record["bytes"] = len(modified)
                record["sha256"] = package.sha256(modified)
        changed = self.rewrite(archive, {
            "laco-laoshifu/" + name: modified,
            "laco-laoshifu/bundle-manifest.json": json.dumps(manifest).encode("utf-8"),
        })
        with self.assertRaisesRegex(ValueError, "Original snapshot"):
            package.read_archive(changed)


if __name__ == "__main__":
    unittest.main()
