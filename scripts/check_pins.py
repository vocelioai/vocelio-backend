#!/usr/bin/env python
"""
Fail if any service requirements.txt re-pin a package managed in constraints.txt.
Usage:
  python scripts/check_pins.py [--root requirements.txt] [--constraints constraints.txt]
CI Integration:
  python scripts/check_pins.py
"""
from __future__ import annotations
import argparse
import pathlib
import re
import sys
from typing import Dict, List, Tuple

PIN_REGEX = re.compile(r"^(?P<name>[A-Za-z0-9_.\-]+)(?P<extras>\[[^\]]+\])?==(?P<version>[^#\s]+)")
REQ_PIN_REGEX = re.compile(r"^(?P<name>[A-Za-z0-9_.\-]+)(?P<extras>\[[^\]]+\])?==")
COMMENT_OR_EMPTY = re.compile(r"^\s*(#.*)?$")
CONSTRAINT_INCLUDE = re.compile(r"^-c\s+")
ALLOWED_OVERRIDES: List[str] = []


def normalize_name(name: str) -> str:
    return name.lower().replace('_', '-')


def _read_lines(path: pathlib.Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        # Fallback with replacement to avoid hard failure on stray encoding
        return path.read_text(encoding="utf-8", errors="replace").splitlines()


def parse_constraints(path: pathlib.Path) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    if not path.exists():
        return pins
    for line in _read_lines(path):
        if COMMENT_OR_EMPTY.match(line):
            continue
        m = PIN_REGEX.match(line.strip())
        if not m:
            continue
        base = normalize_name(m.group('name'))
        pins[base] = m.group('version')
    return pins


def scan_requirements(req_file: pathlib.Path, managed: Dict[str, str]) -> List[Tuple[str, str]]:
    violations: List[Tuple[str, str]] = []
    for raw in _read_lines(req_file):
        line = raw.strip()
        if COMMENT_OR_EMPTY.match(line):
            continue
        if line.startswith('-c '):
            continue
        if line.startswith('-r '):
            continue
        m = REQ_PIN_REGEX.match(line)
        if not m:
            continue
        base = normalize_name(m.group('name'))
        if base in managed and base not in ALLOWED_OVERRIDES:
            violations.append((base, raw))
    return violations


def find_requirement_files(root: pathlib.Path) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    apps = root / 'apps'
    if apps.exists():
        for p in apps.rglob('requirements.txt'):
            files.append(p)
    # Optionally include root requirements
    root_req = root / 'requirements.txt'
    if root_req.exists():
        files.append(root_req)
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--constraints', default='constraints.txt')
    ap.add_argument('--root', default='requirements.txt')
    args = ap.parse_args()

    root = pathlib.Path('.').resolve()
    constraint_path = root / args.constraints

    managed = parse_constraints(constraint_path)
    if not managed:
        print('No constraints found (file missing or empty) – passing by default.')
        return 0

    req_files = find_requirement_files(root)
    overall: Dict[str, List[Tuple[str, str]]] = {}

    for rf in req_files:
        violations = scan_requirements(rf, managed)
        if violations:
            overall[str(rf)] = violations

    if not overall:
        print(f'All clear: no re-pins of managed packages ({len(managed)} managed).')
        return 0

    print('Found re-pins of centrally managed packages:')
    for file, rows in overall.items():
        print(f'\n{file}:')
        for base, raw in rows:
            print(f'  {raw}')
    print('\nManaged packages (from constraints.txt):')
    for k in sorted(managed):
        print(f'  {k}=={managed[k]}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
