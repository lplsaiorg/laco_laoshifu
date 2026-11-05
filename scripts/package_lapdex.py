#!/usr/bin/env python3
"""Build, verify, or install the self-contained Lapdex skill. Python 3.10+."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "laco-laoshifu"
VERSION = "0.1.0"
ARCHIVE_NAME = f"{SKILL_NAME}-lapdex-{VERSION}.zip"
MANIFEST_NAME = "bundle-manifest.json"
RESOURCE_ROOT = "references/kd"
SKILL_NAMES = (
    "kd-context", "kd-data-analysis", "kd-document-writing",
    "kd-knowledge-maintenance", "kd-software-development",
    "laplace-office-standardize",
)
REQUIRED_FILES = {
    "SKILL.md", f"{RESOURCE_ROOT}/AGENTS.md", f"{RESOURCE_ROOT}/source/README.md",
    f"{RESOURCE_ROOT}/source/catalog.json", f"{RESOURCE_ROOT}/source/glossary.json",
    f"{RESOURCE_ROOT}/source/manifest.json", f"{RESOURCE_ROOT}/source/tools/kb.py",
    *(f"{RESOURCE_ROOT}/skills/{name}/SKILL.md" for name in SKILL_NAMES),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: str) -> str:
    """Require portable file names before any extraction is considered."""
    if (not isinstance(value, str) or not value or "\\" in value
            or any(ord(char) < 32 for char in value)):
        raise ValueError(f"Invalid relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        raise ValueError(f"Non-canonical relative path: {value!r}")
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                *(f"lpt{i}" for i in range(1, 10))}
    for part in path.parts:
        if (part in {".", ".."} or part.endswith((".", " "))
                or any(char in part for char in ':<>"|?*')
                or part.split(".", 1)[0].casefold() in reserved):
            raise ValueError(f"Unsafe relative path: {value!r}")
    return value


def is_link(path: Path) -> bool:
    # Junctions on Windows are reparse points, but are not symlinks on Python 3.10.
    attrs = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def source_files(directory: Path):
    if not directory.is_dir() or is_link(directory):
        raise ValueError(f"Expected a real source directory: {directory}")
    for current, dirs, files in os.walk(directory, followlinks=False):
        parent = Path(current)
        dirs[:] = sorted(name for name in dirs
                         if name != "__pycache__" and not is_link(parent / name))
        for name in sorted(files):
            path = parent / name
            if path.suffix in {".pyc", ".pyo"} or is_link(path):
                continue
            if not path.is_file():
                raise ValueError(f"Expected a regular source file: {path}")
            yield path


def collect_payload(repo_root: Path) -> dict[str, bytes]:
    repo_root = Path(repo_root).resolve()
    entry = repo_root / "integrations" / "lapdex" / "SKILL.md"
    agents = entry.with_name("AGENTS.md")
    for path in (entry, agents):
        if not path.is_file() or is_link(path):
            raise ValueError(f"Required source file missing or linked: {path}")
    payload = {"SKILL.md": entry.read_bytes(), f"{RESOURCE_ROOT}/AGENTS.md": agents.read_bytes()}
    directories = [repo_root / "source"]
    directories.extend(repo_root / "skills" / name for name in SKILL_NAMES)
    for directory in directories:
        for path in source_files(directory):
            relative = safe_relative(f"{RESOURCE_ROOT}/" + path.relative_to(repo_root).as_posix())
            payload[relative] = path.read_bytes()
    validate_payload(payload)
    return payload


def validate_payload(payload: dict[str, bytes]) -> int:
    missing = REQUIRED_FILES - payload.keys()
    if missing:
        raise ValueError(f"Required payload files missing: {', '.join(sorted(missing))}")
    case_names = set()
    for name in payload:
        safe_relative(name)
        if name.casefold() in case_names:
            raise ValueError(f"Case-insensitive path collision: {name}")
        case_names.add(name.casefold())
    entry = payload["SKILL.md"].decode("utf-8-sig")
    if not re.search(r"(?m)^name:\s*laco-laoshifu\s*$", entry):
        raise ValueError("The Lapdex entry must declare name: laco-laoshifu")
    original_manifest = json.loads(payload[f"{RESOURCE_ROOT}/source/manifest.json"].decode("utf-8-sig"))
    snapshots = original_manifest.get("files")
    if not isinstance(snapshots, list) or not snapshots:
        raise ValueError("The original source manifest contains no snapshot files")
    seen = set()
    for record in snapshots:
        relative = safe_relative(record["path"])
        if not relative.startswith("references/kd/") or relative.casefold() in seen:
            raise ValueError(f"Invalid or duplicate original snapshot path: {relative}")
        seen.add(relative.casefold())
        name = f"{RESOURCE_ROOT}/source/" + relative
        data = payload.get(name)
        if (data is None or len(data) != record["bytes"]
                or sha256(data) != record["sha256"]):
            raise ValueError(f"Original snapshot checksum mismatch: {name}")
    return len(snapshots)


def source_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, timeout=5, check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    commit = result.stdout.strip()
    return commit if re.fullmatch(r"[0-9a-f]{40,64}", commit) else None


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def read_archive(archive: Path) -> tuple[dict, dict[str, bytes]]:
    """Return verified bytes; callers must not use ZipFile.extractall()."""
    payload = {}
    seen = set()
    manifest_data = None
    prefix = SKILL_NAME + "/"
    try:
        with zipfile.ZipFile(archive) as package:
            for info in package.infolist():
                name = safe_relative(info.filename)
                if info.is_dir() or not name.startswith(prefix):
                    raise ValueError(f"Unexpected archive entry: {name}")
                relative = safe_relative(name[len(prefix):])
                if name.casefold() in seen:
                    raise ValueError(f"Duplicate or case-conflicting archive entry: {name}")
                seen.add(name.casefold())
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_IFMT(mode) not in {0, stat.S_IFREG}:
                    raise ValueError(f"Archive links or special files are not allowed: {name}")
                if info.flag_bits & 1:
                    raise ValueError("Encrypted archive entries are not supported")
                data = package.read(info)
                if relative == MANIFEST_NAME:
                    manifest_data = data
                else:
                    payload[relative] = data
    except (zipfile.BadZipFile, RuntimeError) as error:
        raise ValueError(f"Cannot read skill archive: {error}") from error
    if manifest_data is None:
        raise ValueError(f"Archive is missing {MANIFEST_NAME}")
    manifest = json.loads(manifest_data.decode("utf-8"))
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1
            or manifest.get("name") != SKILL_NAME or manifest.get("version") != VERSION):
        raise ValueError("Unrecognized bundle manifest identity or version")
    records = manifest.get("files")
    if not isinstance(records, list):
        raise ValueError("Bundle manifest files must be an array")
    expected = set()
    expected_case = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid bundle manifest record")
        relative = safe_relative(record.get("path"))
        if relative == MANIFEST_NAME or relative.casefold() in expected_case:
            raise ValueError(f"Duplicate or invalid manifest path: {relative}")
        expected.add(relative)
        expected_case.add(relative.casefold())
        data = payload.get(relative)
        size = record.get("bytes")
        digest = record.get("sha256")
        if (type(size) is not int or size < 0 or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ValueError(f"Invalid manifest checksum or size: {relative}")
        if data is None or len(data) != size or sha256(data) != digest:
            raise ValueError(f"Bundle payload checksum mismatch: {relative}")
    if payload.keys() != expected:
        raise ValueError("Bundle manifest does not enumerate every payload file")
    validate_payload(payload)
    return manifest, payload


def build_archive(output: Path, *, repo_root: Path = REPO_ROOT, force=False) -> Path:
    repo_root = Path(repo_root).resolve()
    output = Path(output).expanduser().resolve()
    if any(output.is_relative_to(repo_root / name) for name in ("source", "skills")):
        raise ValueError("Build output must be outside the source and skills trees")
    archive = output / ARCHIVE_NAME
    checksum = output / (ARCHIVE_NAME + ".sha256")
    if not force and (archive.exists() or checksum.exists()):
        raise FileExistsError(f"Output already exists; use --force to rebuild: {archive}")
    if archive.is_symlink() or checksum.is_symlink():
        raise ValueError("Refusing to replace a linked output file")
    payload = collect_payload(repo_root)
    manifest = {
        "schema_version": 1, "name": SKILL_NAME, "version": VERSION,
        "source_commit": source_commit(repo_root),
        "files": [{"path": name, "bytes": len(data), "sha256": sha256(data)}
                  for name, data in sorted(payload.items())],
    }
    output.mkdir(parents=True, exist_ok=True)
    # All temporary files live below the explicitly selected output directory.
    with tempfile.TemporaryDirectory(prefix=".lapdex-build-", dir=output) as temporary:
        stage = Path(temporary) / ARCHIVE_NAME
        with zipfile.ZipFile(stage, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
            for name, data in sorted(payload.items()):
                package.writestr(zip_info(f"{SKILL_NAME}/{name}"), data)
            package.writestr(zip_info(f"{SKILL_NAME}/{MANIFEST_NAME}"),
                             json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
        read_archive(stage)
        checksum_stage = Path(temporary) / checksum.name
        checksum_stage.write_text(f"{sha256(stage.read_bytes())}  {archive.name}\n", encoding="ascii")
        if not force and (archive.exists() or checksum.exists()):
            raise FileExistsError(f"Output appeared during build: {archive}")
        os.replace(stage, archive)
        os.replace(checksum_stage, checksum)
    return archive


def install_archive(archive: Path, skills_dir: Path, *, dry_run=False) -> Path:
    manifest, payload = read_archive(Path(archive))
    skills_dir = Path(skills_dir).expanduser().resolve()
    target = skills_dir / SKILL_NAME
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Skill already exists; choose a clean skills directory: {target}")
    if dry_run:
        return target
    skills_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".lapdex-install-", dir=skills_dir) as temporary:
        stage = Path(temporary) / SKILL_NAME
        stage.mkdir()
        all_files = {**payload, MANIFEST_NAME: json.dumps(
            manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"}
        for relative, data in all_files.items():
            destination = stage / relative
            if not destination.resolve().is_relative_to(stage.resolve()):
                raise ValueError(f"Install path escapes staging directory: {relative}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Skill appeared during install: {target}")
        # Same-parent staging avoids cross-volume moves and partial installations.
        stage.rename(target)
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", type=Path, metavar="ZIP", help="verify an existing bundle")
    action.add_argument("--install", type=Path, metavar="ZIP", help="install a verified bundle")
    parser.add_argument("--output", type=Path, help="build output directory (default: repo/dist)")
    parser.add_argument("--force", action="store_true", help="replace this version's two build outputs")
    parser.add_argument("--skills-dir", type=Path,
                        help="Lapdex skills directory (default: ~/.lapdex/skills)")
    parser.add_argument("--dry-run", action="store_true", help="validate installation without writing")
    args = parser.parse_args(argv)
    if (args.check or args.install) and (args.output or args.force):
        parser.error("--output and --force apply only when building")
    if not args.install and (args.skills_dir or args.dry_run):
        parser.error("--skills-dir and --dry-run require --install")
    try:
        if args.check:
            manifest, payload = read_archive(args.check)
            print(f"Verified {manifest['name']} {manifest['version']}: "
                  f"{len(payload)} payload files; original snapshot checksums match.")
        elif args.install:
            target = install_archive(args.install, args.skills_dir or Path.home() / ".lapdex" / "skills",
                                     dry_run=args.dry_run)
            print(f"{'Would install' if args.dry_run else 'Installed'}: {target}")
        else:
            archive = build_archive(args.output or REPO_ROOT / "dist", force=args.force)
            print(f"Built: {archive}")
            print(f"SHA-256: {archive.with_name(archive.name + '.sha256')}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
