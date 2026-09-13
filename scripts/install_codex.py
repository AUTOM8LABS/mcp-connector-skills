#!/usr/bin/env python3
"""Install complete skill folders into Codex's local discovery directory.

Standard library only. Existing different folders are never overwritten.
--update replaces only an unchanged, installer-owned copy and retains a backup.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
STAMP = '.mcp-connector-install.json'
SOURCE = 'AUTOM8LABS/mcp-connector-skills'
PUBLIC_SKILL_FILES = frozenset({'SKILL.md', 'agents/openai.yaml'})


def discover(root):
    """Use the reviewed public marketplace as the distribution allowlist.

    New folders must never become public packages merely by existing locally.
    """
    skills = {}
    marketplace = json.loads((root / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    if not isinstance(marketplace, dict) or not isinstance(marketplace.get('plugins'), list):
        raise ValueError('Marketplace must contain a plugins list')
    for plugin in marketplace['plugins']:
        if not isinstance(plugin, dict):
            raise ValueError('Marketplace plugin must be an object')
        name = plugin.get('name')
        source = plugin.get('source')
        if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in skills:
            raise ValueError(f'Invalid or duplicate skill folder: {name}')
        if not isinstance(source, str) or not re.fullmatch(r'\./[a-z0-9]+(?:-[a-z0-9]+)*', source):
            raise ValueError(f'Invalid public plugin source: {source}')
        folder = root / source / 'skills' / name
        if not folder.resolve().is_relative_to(root.resolve()) or not (folder / 'SKILL.md').is_file():
            raise ValueError(f'Missing or external public skill: {name}')
        extra = set(fingerprint(folder)) - PUBLIC_SKILL_FILES
        if extra:
            raise ValueError(f'Extra files in public skill {name}: {", ".join(sorted(extra))}. '
                             'Keep supporting documents in a separate private repository.')
        skills[name] = folder
    if not skills:
        raise ValueError(f'No skills found in {root}')
    return dict(sorted(skills.items()))


def fingerprint(folder):
    """Hash the entire payload, refusing links and unexpected filesystem objects."""
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError(f'Expected a real skill directory: {folder}')
    hashes = {}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink not supported in a copied skill: {path}')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f'Not a regular file: {path}')
        if path.relative_to(folder).as_posix() != STAMP:
            hashes[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def plan_install(root, destination, names=None, update=False):
    skills = discover(root)
    selected = sorted(set(names or skills))
    unknown = set(selected) - skills.keys()
    if unknown:
        raise ValueError('Unknown skills: ' + ', '.join(sorted(unknown)))
    destination = destination.expanduser().resolve()
    plan = []
    for name in selected:
        source = skills[name]
        target = destination / name
        if destination == source.resolve() or source.resolve() in destination.parents:
            raise ValueError('Destination must not be inside a source skill')
        if target.resolve() == source.resolve():
            raise ValueError('Destination must not be the source skill')
        payload = fingerprint(source)
        previous = None
        action = 'install'
        if target.exists() or target.is_symlink():
            previous = fingerprint(target)
            if previous == payload:
                action = 'unchanged'
            elif update:
                stamp = target / STAMP
                try:
                    record = json.loads(stamp.read_text(encoding='utf-8'))
                except (OSError, ValueError) as exc:
                    raise ValueError(f'Not an installer-owned copy: {target}') from exc
                if not isinstance(record, dict) or record.get('source') != SOURCE or record.get('files') != previous:
                    raise ValueError(f'Local changes or invalid ownership record: {target}')
                action = 'update'
            else:
                raise ValueError(f'Different skill already exists: {target}. Use --update for an unchanged installer-owned copy, or choose another destination.')
        plan.append((action, source, target, payload, previous))
    return plan


def install(root, destination, names=None, update=False, dry_run=False):
    # Preflight every selected skill before writing any of them.
    plan = plan_install(root, destination, names, update)
    for action, source, target, payload, previous in plan:
        print(f'{"Would " if dry_run else ""}{action}: {target}')
        if dry_run or action == 'unchanged':
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.connector-stage-', dir=target.parent) as temp:
            staged = Path(temp) / target.name
            shutil.copytree(source, staged)
            if fingerprint(staged) != payload:
                raise ValueError(f'Source changed during install: {source}')
            (staged / STAMP).write_text(json.dumps({'source': SOURCE, 'files': payload}, indent=2) + '\n', encoding='utf-8')
            backup = None
            if action == 'update':
                if fingerprint(target) != previous:
                    raise ValueError(f'Destination changed during install: {target}')
                backup_root = target.parent / '.connector-backups'
                if backup_root.is_symlink():
                    raise ValueError(f'Backup directory must not be a symlink: {backup_root}')
                backup_root.mkdir(exist_ok=True)
                # ZIP backups contain no discoverable SKILL.md directories.
                archive = backup_root / f'{target.name}-{uuid.uuid4().hex}.zip'
                shutil.make_archive(str(archive.with_suffix('')), 'zip', root_dir=target.parent, base_dir=target.name)
                backup = Path(temp) / 'previous'
                target.rename(backup)
                print(f'Backup: {archive}')
            elif target.exists() or target.is_symlink():
                raise ValueError(f'Destination appeared during install: {target}')
            try:
                staged.rename(target)
            except OSError:
                if backup is not None:
                    backup.rename(target)
                raise
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=Path.home() / '.agents' / 'skills', help='Skill discovery directory (default: ~/.agents/skills)')
    parser.add_argument('--skill', action='append', choices=sorted(discover(ROOT)), help='Install only this skill; repeat to select several (default: all)')
    parser.add_argument('--update', action='store_true', help='Update unchanged installer-owned copies, retaining ZIP backups')
    parser.add_argument('--dry-run', action='store_true', help='Check all destinations and print actions without writing')
    args = parser.parse_args()
    try:
        install(ROOT, args.dest, args.skill, args.update, args.dry_run)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Installation stopped: {exc}\n')


if __name__ == '__main__':
    main()
