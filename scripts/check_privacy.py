#!/usr/bin/env python3
"""Check tracked release resources or ZIPs for local paths and identity metadata."""
import argparse
import io
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

LOCAL_PATH = re.compile(r"(?i)(?<![a-z])[a-z]:[\\/]+|file:/+|/(?:Users|home)/[\w.-]+/")
PRIVATE_FILE = re.compile(r"(?i)(?:^|/)(?:private-memory/|\.env$|auth\.json$|id_rsa$)")
SECRET = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}|\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}")

def inspect(name, data):
    findings = []
    if PRIVATE_FILE.search(name):
        findings.append((name, "private file"))
    if SECRET.search(data):
        findings.append((name, "credential pattern"))
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for item in archive.infolist():
                if not item.is_dir():
                    findings.extend(inspect(name + "!" + item.filename, archive.read(item)))
        return findings
    suffix = Path(name).suffix.lower()
    if suffix in (".md", ".json", ".xml", ".rels", ".svg", ".txt"):
        text = data.decode("utf-8-sig", "replace")
        if LOCAL_PATH.search(text):
            findings.append((name, "absolute local path"))
        if name.endswith("docProps/core.xml"):
            root = ET.fromstring(data)
            if any(el.tag.split("}")[-1] in ("creator", "lastModifiedBy")
                   and (el.text or "").strip() for el in root):
                findings.append((name, "document identity"))
        if suffix == ".rels" and "/attachedTemplate" in text:
            findings.append((name, "external template"))
    if suffix == ".pdf":
        if re.search(rb"/Author\s*(?:\(|<)", data):
            findings.append((name, "PDF author"))
    return findings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="files to check; default is git tracked files")
    args = parser.parse_args()
    paths = args.paths
    if not paths:
        names = subprocess.check_output(["git", "ls-files", "-z"]).decode("utf-8").split("\0")
        paths = [Path(name) for name in names if name]
    findings = []
    for path in paths:
        if path.is_file():
            findings.extend(inspect(path.as_posix(), path.read_bytes()))
    for name, reason in findings:
        print(f"{name}: {reason}")
    print(f"Checked {len(paths)} files, {len(findings)} findings")
    return bool(findings)

if __name__ == "__main__":
    sys.exit(main())
