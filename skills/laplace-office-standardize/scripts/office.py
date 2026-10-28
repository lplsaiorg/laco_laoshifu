#!/usr/bin/env python3
"""Apply Laplace Office styles and the supplied logo using native Microsoft Office."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import posixpath
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET

SKILL = Path(__file__).resolve().parents[1]
SUPPORTED = {'.docx': 'word', '.xlsx': 'excel', '.pptx': 'powerpoint'}
OTHER_OFFICE = {'.doc', '.xls', '.ppt', '.docm', '.xlsm', '.pptm', '.xlsb'}
TEMPLATES = {'word': ('word.dotx', '.dotx'), 'excel': ('excel.xltx', '.xltx'),
             'powerpoint': ('powerpoint.potx', '.potx')}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    with Path(path).open('rb') as stream:
        result = hashlib.file_digest(stream, 'sha256') if hasattr(hashlib, 'file_digest') else None
        if result is not None:
            return result.hexdigest()
        return hashlib.sha256(stream.read()).hexdigest()


def png_size(path):
    with Path(path).open('rb') as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Logo must be a PNG file; retain the original aspect ratio.')
    return struct.unpack('>II', header[16:24])


def load_profile(path, require_templates=True):
    path = Path(path).resolve(strict=True)
    profile = read_json(path)
    if profile.get('schema_version') != 1 or profile.get('approval_status') not in {'draft', 'approved'}:
        raise ValueError('Profile needs schema_version=1 and approval_status=draft or approved.')
    profile['logo'] = str((path.parent / profile['logo']).resolve(strict=True))
    width, height = png_size(profile['logo'])
    if not width or not height or not 8 <= float(profile['logo_width_pt']) <= 144:
        raise ValueError('Invalid logo dimensions or logo_width_pt (8..144).')
    for kind, (_, extension) in TEMPLATES.items():
        raw = profile[kind].get('template')
        if raw:
            target = (path.parent / raw).resolve()
            modern_extension = next(ext for ext, format_name in SUPPORTED.items() if format_name == kind)
            if target.suffix.lower() not in {extension, modern_extension}:
                raise ValueError(f'Unsupported template file: {target}')
            if require_templates and not target.is_file():
                raise ValueError(f'Template missing: {target}; run templates first or select a complete profile.')
            profile[kind]['template'] = str(target)
    profile['_path'] = str(path)
    return profile, width, height


def powershell():
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
    for path in [shutil.which('pwsh'), str(bundled), shutil.which('powershell')]:
        if path and Path(path).is_file():
            return str(path)
    raise ValueError('PowerShell is required on Windows.')


def doctor(profile_path):
    profile, width, height = load_profile(profile_path, False)
    result = {'platform': sys.platform, 'profile': profile['_path'],
              'approval_status': profile['approval_status'], 'logo_pixels': [width, height],
              'logo_sha256': digest(profile['logo']), 'office': {}, 'powershell': None}
    if sys.platform == 'win32':
        import winreg
        result['powershell'] = powershell()
        for kind, prog_id in [('word', 'Word.Application'), ('excel', 'Excel.Application'), ('powerpoint', 'PowerPoint.Application')]:
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, prog_id):
                    result['office'][kind] = True
            except OSError:
                result['office'][kind] = False
    result['templates'] = {kind: bool(profile[kind].get('template') and Path(profile[kind]['template']).is_file())
                           for kind in TEMPLATES}
    return result


def validate_package(path):
    with zipfile.ZipFile(path) as package:
        if package.testzip() is not None:
            raise ValueError('Corrupt Office ZIP package.')
        names = package.namelist()
        if '[Content_Types].xml' not in names:
            raise ValueError('Not a valid Office Open XML package.')
        for name in names:
            if name.endswith(('.xml', '.rels')):
                ET.fromstring(package.read(name))
        if any('vbaProject' in name or '_xmlsignatures/' in name for name in names):
            raise ValueError('Macro-bearing or digitally signed documents require a separate preservation workflow.')
        if 'xl/connections.xml' in names or any(name.startswith('xl/externalLinks/') for name in names):
            raise ValueError('External-data workbooks require a separate refresh/preservation workflow.')
        return {'parts': len(names), 'charts': sum(name.startswith(('word/charts/', 'xl/charts/', 'ppt/charts/'))
                                                 and name.endswith('.xml') for name in names),
                'embeddings': {name: hashlib.sha256(package.read(name)).hexdigest()
                               for name in names if '/embeddings/' in name}}


def validate_word_logo(path):
    """Every active header story must have exactly one of this tool's logos."""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
          'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
    def enabled(node):
        return node is not None and node.get('{'+ns['w']+'}val', 'true') not in {'0','false','off'}
    with zipfile.ZipFile(path) as package:
        rels = ET.fromstring(package.read('word/_rels/document.xml.rels'))
        targets = {node.get('Id'): posixpath.normpath(posixpath.join('word', node.get('Target', '')))
                   for node in rels}
        settings = ET.fromstring(package.read('word/settings.xml')) if 'word/settings.xml' in package.namelist() else None
        even = settings is not None and enabled(settings.find('w:evenAndOddHeaders', ns))
        document = ET.fromstring(package.read('word/document.xml'))
        if any(node.get('descr') == 'LaplaceDocs.CompanyLogo' for node in document.findall('.//wp:docPr', ns)):
            raise ValueError('Word logo is anchored in the body instead of a header.')
        active_refs = {}
        for section in document.findall('.//w:sectPr', ns):
            for ref in section.findall('w:headerReference', ns):
                active_refs[ref.get('{'+ns['w']+'}type')] = targets.get(ref.get('{'+ns['r']+'}id'))
            required = ['default'] + (['first'] if enabled(section.find('w:titlePg', ns)) else []) + (['even'] if even else [])
            for kind in required:
                target = active_refs.get(kind)
                if not target or target not in package.namelist():
                    raise ValueError(f'Word {kind} header missing for company logo.')
                header = ET.fromstring(package.read(target))
                count = sum(node.get('descr') == 'LaplaceDocs.CompanyLogo' for node in header.findall('.//wp:docPr', ns))
                if count != 1:
                    raise ValueError(f'Word {kind} header must contain exactly one managed company logo; got {count}.')


def collect_inputs(inputs, output, recursive=False):
    """Retain folder structure and reject overwrites/collisions before starting Office."""
    output = Path(output).resolve()
    jobs, seen = [], set()
    for value in inputs:
        source = Path(value).resolve(strict=True)
        files = sorted(source.rglob('*') if recursive else source.glob('*')) if source.is_dir() else [source]
        for path in files:
            if not path.is_file() or path.name.startswith('~$'):
                continue
            if source.is_dir() and path.is_relative_to(output):
                continue
            if path.suffix.lower() not in SUPPORTED:
                if not source.is_dir():
                    raise ValueError(f'Unsupported file: {path}; supported: .docx .xlsx .pptx. Convert legacy files with Office first.')
                continue
            rel = path.relative_to(source) if source.is_dir() else Path(path.name)
            target = output / rel
            if path == target or target.exists():
                raise ValueError(f'Output would overwrite an existing file: {target}')
            key = str(target).casefold()
            if key in seen:
                raise ValueError(f'Colliding output paths: {target}; use separate output folders.')
            seen.add(key)
            jobs.append((path, target, SUPPORTED[path.suffix.lower()]))
    if not jobs:
        raise ValueError('No .docx/.xlsx/.pptx inputs found.')
    return jobs


def worker(profile, path, kind, temp, width, height, mode='apply', pdf=None, timeout=180):
    job_path = temp / 'job.json'
    result_path = temp / 'result.json'
    write_json(job_path, {'mode': mode, 'path': str(path), 'format': kind, 'profile': profile,
                          'logo_width': width, 'logo_height': height, 'pdf': str(pdf) if pdf else None})
    command = [powershell(), '-NoLogo', '-NoProfile', '-NonInteractive', '-File',
               str(SKILL / 'scripts/office_worker.ps1'), '-JobPath', str(job_path), '-ResultPath', str(result_path)]
    completed = subprocess.run(command, capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
    if result_path.exists():
        result = read_json(result_path)
        if completed.returncode != 0:
            result['success'] = False
        return result
    return {'success': False, 'content_unchanged': False,
            'error': (completed.stderr or completed.stdout or 'Office worker returned no result.')[-2000:], 'notes': []}


def create_templates(profile_path):
    profile, width, height = load_profile(profile_path, False)
    results = []
    for kind, (_, extension) in TEMPLATES.items():
        destination = Path(profile[kind]['template'])
        if destination.exists():
            validate_package(destination)
        if destination.suffix.lower() != extension:
            raise ValueError(f'Template generation requires {extension}: {destination}')
    for kind in TEMPLATES:
        destination = Path(profile[kind]['template'])
        if destination.exists():
            results.append({'format': kind, 'path': str(destination), 'success': True, 'status': 'existing_template_kept'})
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='laplace-template-') as folder:
            temp = Path(folder)
            draft = temp / destination.name
            result = worker(profile, draft, kind, temp, width, height, mode='template', pdf=draft.with_suffix('.pdf'))
            if not result['success']:
                raise ValueError(f'{kind}: {result.get("error")}')
            validate_package(draft)
            shutil.copy2(draft, destination)
            # Template previews are review assets, not substitutes for an approved company template.
            if draft.with_suffix('.pdf').exists():
                shutil.copy2(draft.with_suffix('.pdf'), destination.with_suffix('.pdf'))
            results.append({'format': kind, 'path': str(destination), **result})
    return results


def apply(inputs, output, profile_path, recursive=False, dry_run=False, pdf=False):
    profile, width, height = load_profile(profile_path)
    jobs = collect_inputs(inputs, output, recursive)
    if pdf:
        for _, destination, _ in jobs:
            preview = destination.with_name(destination.name + '.review.pdf')
            if preview.exists():
                raise ValueError(f'PDF preview would overwrite an existing file: {preview}')
    report = {'schema_version': 1, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'profile': profile['_path'], 'profile_version': profile['version'],
              'approval_status': profile['approval_status'], 'dry_run': dry_run, 'files': []}
    # Never silently omit legacy/macro files from an otherwise supported batch.
    for value in inputs:
        root = Path(value).resolve()
        if root.is_dir():
            for item in sorted(root.rglob('*') if recursive else root.glob('*')):
                if (item.is_file() and item.suffix.lower() in OTHER_OFFICE and not item.name.startswith('~$')
                        and not item.is_relative_to(Path(output).resolve())):
                    report['files'].append({'input': str(item), 'status': 'unsupported_conversion_required',
                                            'error': 'Convert legacy files or use a macro-preserving workflow first.'})
    if dry_run:
        report['files'].extend({'input': str(src), 'output': str(dst), 'format': kind, 'status': 'planned'}
                               for src, dst, kind in jobs)
        return report
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / 'standardization-report.json'
    if report_path.exists():
        raise ValueError(f'Report exists; choose a new output folder: {report_path}')
    for source, destination, kind in jobs:
        record = {'input': str(source), 'output': str(destination), 'format': kind, 'status': 'failed'}
        try:
            original_hash = digest(source)
            before = validate_package(source)
            with tempfile.TemporaryDirectory(prefix='laplace-office-') as folder:
                temp = Path(folder)
                working = temp / source.name
                shutil.copy2(source, working)
                pdf_path = working.with_suffix('.pdf') if pdf else None
                result = worker(profile, working, kind, temp, width, height, pdf=pdf_path)
                record.update(result)
                if not result['success'] or not result['content_unchanged']:
                    raise ValueError(result.get('error') or 'Content preservation check failed.')
                after = validate_package(working)
                if before['charts'] != after['charts']:
                    raise ValueError('The number of chart parts changed; output withheld for review.')
                if before['embeddings'] != after['embeddings']:
                    raise ValueError('Embedded objects changed; output withheld for a dedicated preservation workflow.')
                if kind == 'word':
                    validate_word_logo(working)
                if digest(source) != original_hash:
                    raise ValueError('Source changed during processing; output withheld.')
                destination.parent.mkdir(parents=True, exist_ok=True)
                # Exclusive creation prevents a late-arriving file from being overwritten.
                with destination.open('xb') as stream, working.open('rb') as incoming:
                    shutil.copyfileobj(incoming, stream)
                record['sha256'] = digest(destination)
                record['source_sha256'] = original_hash
                record['status'] = 'processed_needs_visual_review'
                if pdf_path and pdf_path.exists():
                    preview = destination.with_name(destination.name + '.review.pdf')
                    with preview.open('xb') as stream, pdf_path.open('rb') as incoming:
                        shutil.copyfileobj(incoming, stream)
                    record['preview_pdf'] = str(preview)
        except (OSError, ValueError, subprocess.TimeoutExpired, zipfile.BadZipFile, ET.ParseError) as exc:
            record['success'] = False
            record['error'] = str(exc)
        report['files'].append(record)
        write_json(report_path, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, default=SKILL / 'assets/company-profile.json')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('doctor', help='Read-only dependency/profile check; does not launch Office.')
    commands.add_parser('templates', help='Create the missing draft DOTX/XLTX/POTX plus PDF review copies.')
    cmd = commands.add_parser('apply', help='Standardize copies of modern Office files.')
    cmd.add_argument('inputs', nargs='+', type=Path)
    cmd.add_argument('--output', required=True, type=Path)
    cmd.add_argument('--recursive', action='store_true')
    cmd.add_argument('--dry-run', action='store_true')
    cmd.add_argument('--pdf', action='store_true', help='Also export PDF review copies with native Office.')
    args = parser.parse_args(argv)
    try:
        if args.command == 'doctor':
            result = doctor(args.profile)
        elif sys.platform != 'win32':
            raise ValueError('This native template workflow requires Windows and installed Microsoft Office.')
        elif args.command == 'templates':
            result = create_templates(args.profile)
        else:
            result = apply(args.inputs, args.output, args.profile, args.recursive, args.dry_run, args.pdf)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and any(f.get('status') in {'failed','unsupported_conversion_required'} for f in result.get('files', [])) else 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
