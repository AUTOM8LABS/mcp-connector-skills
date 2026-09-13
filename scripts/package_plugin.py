#!/usr/bin/env python3
"""Build a plugin folder and ZIP containing the eight connector skills."""

import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from install_codex import ROOT, fingerprint
from validate_skills import validate


def package_plugin(root, output):
    skills, errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    portable = json.loads((root / 'packaging' / 'plugin.json').read_text(encoding='utf-8'))
    interface = json.loads((root / 'packaging' / 'openai-interface.json').read_text(encoding='utf-8'))
    name = portable.get('name')
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('Invalid plugin name')
    output = output.resolve()
    if any(output == folder.resolve() or folder.resolve() in output.parents for folder in skills.values()):
        raise ValueError('Package output must not be inside a skill folder')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Plugin output must be empty; use a fresh directory')
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.plugin-stage-', dir=output) as temp:
        staged = Path(temp) / name
        staged.mkdir()
        identity = {k: v for k, v in portable.items() if k != '$schema'}
        manifests = {
            'plugin.json': portable,
            '.codex-plugin/plugin.json': {**identity, 'skills': './skills/', 'interface': interface},
            '.claude-plugin/plugin.json': {**identity, 'skills': './skills/'},
        }
        for relative, data in manifests.items():
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        for skill_name, folder in skills.items():
            payload = fingerprint(folder)
            for relative in payload:
                target = staged / 'skills' / skill_name / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(folder / relative, target)
            if fingerprint(staged / 'skills' / skill_name) != payload:
                raise ValueError(f'Source changed during packaging: {skill_name}')
        (staged / 'README.md').write_text(
            '# AUTOM8LABS Operator Skills\n\n'
            'Eight skills for operating AUTOM8LABS MCP Connectors.\n'
            'Install and connect the relevant connector before using a skill.\n\n'
            'Setup: https://github.com/AUTOM8LABS/mcp-connector-skills/blob/main/docs/installation.md\n',
            encoding='utf-8')
        archive = Path(temp) / f'{name}.zip'
        with ZipFile(archive, 'w', ZIP_DEFLATED) as zip_file:
            for relative in fingerprint(staged):
                zip_file.write(staged / relative, f'{name}/{relative}')
        folder = output / name
        staged.rename(folder)
        target_archive = output / archive.name
        archive.rename(target_archive)
    return folder, target_archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / 'plugin')
    args = parser.parse_args()
    try:
        for path in package_plugin(ROOT, args.output):
            print(path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'Plugin packaging failed: {exc}\n')


if __name__ == '__main__':
    main()
