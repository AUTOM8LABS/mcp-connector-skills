#!/usr/bin/env python3
"""Build standalone operator ZIPs with skill instructions and Codex UI metadata."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from install_codex import ROOT, fingerprint
from validate_skills import validate


def package(root, output):
    skills, errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    output = output.resolve()
    if any(output == folder.resolve() or folder.resolve() in output.parents for folder in skills.values()):
        raise ValueError('Package output must not be inside a skill folder')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Package output must be empty; use a fresh directory to avoid stale release assets')
    output.mkdir(parents=True, exist_ok=True)
    archives = []
    for name, folder in skills.items():
        archive = output / f'{name}.zip'
        with ZipFile(archive, 'w', ZIP_DEFLATED) as zip_file:
            for relative in fingerprint(folder):
                zip_file.write(folder / relative, f'{name}/{relative}')
        archives.append(archive)
    return archives


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    try:
        for archive in package(ROOT, args.output):
            print(archive)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Packaging failed: {exc}\n')


if __name__ == '__main__':
    main()
