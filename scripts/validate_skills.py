#!/usr/bin/env python3
"""Validate portable skill metadata, local references, and Claude packaging."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml

from install_codex import ROOT, discover, fingerprint


def validate_skill(folder):
    errors = []
    try:
        fingerprint(folder)
        text = (folder / 'SKILL.md').read_text(encoding='utf-8')
        match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
        if not match:
            raise ValueError('Missing YAML frontmatter')
        metadata = yaml.safe_load(match.group(1))
        if not isinstance(metadata, dict):
            raise ValueError('Frontmatter must be a mapping')
        name = metadata.get('name')
        if name != folder.name or len(name) > 64 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            errors.append('name must match the skill folder and use lowercase hyphenated words')
        desc = metadata.get('description')
        if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
            errors.append('description must be a nonempty string of at most 1024 characters')
        if not text[match.end():].strip():
            errors.append('Missing skill instructions')
        if re.search(r'\[TODO:', text):
            errors.append('Unfinished scaffold placeholder')
        interface = yaml.safe_load((folder / 'agents' / 'openai.yaml').read_text(encoding='utf-8'))
        if not isinstance(interface, dict) or not isinstance(interface.get('interface'), dict):
            raise ValueError('openai.yaml must contain an interface mapping')
        ui = interface['interface']
        for key in ('display_name', 'short_description', 'default_prompt'):
            if not isinstance(ui.get(key), str) or not ui[key].strip():
                errors.append(f'interface.{key} must be a nonempty string')
        short = ui.get('short_description', '')
        if isinstance(short, str) and not 25 <= len(short) <= 64:
            errors.append('short_description must be 25–64 characters')
        prompt = ui.get('default_prompt')
        if isinstance(prompt, str) and f'${name}' not in prompt:
            errors.append('default_prompt must invoke this skill by name')

        # Validate local Markdown links plus code-formatted .md reference paths.
        # Each skill must remain usable when installed without its siblings.
        reachable = set()
        pending = [folder / 'SKILL.md']
        while pending:
            document = pending.pop()
            if document in reachable:
                continue
            reachable.add(document)
            body = document.read_text(encoding='utf-8')
            links = re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)', body)
            links += re.findall(r'`((?:references/)?[a-zA-Z0-9_./-]+\.md)`', body)
            for link in set(links):
                parsed = urlsplit(link.strip('<>'))
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (document.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(folder.resolve()):
                    errors.append(f'{document.name}: reference escapes skill: {link}')
                elif not target.is_file():
                    errors.append(f'{document.name}: missing reference: {link}')
                elif target.suffix == '.md':
                    pending.append(target)
        orphaned = {p.resolve() for p in (folder / 'references').rglob('*.md')} - {p.resolve() for p in reachable}
        errors.extend(f'Unreachable reference: {p.name}' for p in sorted(orphaned))
    except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
        errors.append(str(exc))
    return errors


def validate(root):
    errors = []
    skills = discover(root)
    for name, folder in skills.items():
        errors.extend(f'{name}: {error}' for error in validate_skill(folder))
    marketplace = json.loads((root / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    listed = set()
    for plugin in marketplace['plugins']:
        product = (root / plugin['source']).resolve()
        if not product.is_relative_to(root.resolve()):
            errors.append(f'Marketplace path escapes repository: {plugin["source"]}')
            continue
        manifest = json.loads((product / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
        name = plugin['name']
        if name in listed or manifest['name'] != name:
            errors.append(f'Duplicate or mismatched plugin: {name}')
        listed.add(name)
        expected = product / 'skills' / name
        if name not in skills or expected.resolve() != skills[name].resolve():
            errors.append(f'Plugin does not resolve to its skill: {name}')
        if not re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')):
            errors.append(f'Invalid plugin version: {name}')
    if listed != skills.keys():
        errors.append('Marketplace and skill inventory differ')
    return skills, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        skills, errors = validate(args.root.resolve())
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        parser.exit(1, f'Validation failed: {exc}\n')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(skills)} skills, Codex metadata, portable references, and Claude manifests')
    return 0


if __name__ == '__main__':
    sys.exit(main())
