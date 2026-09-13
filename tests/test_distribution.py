import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from install_codex import ROOT, STAMP, discover, fingerprint, install
from package_skills import package
from package_plugin import package_plugin
from validate_skills import validate, validate_skill


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        for folder in discover(ROOT).values():
            shutil.copytree(folder, self.source / folder.relative_to(ROOT))
        shutil.copytree(ROOT / '.claude-plugin', self.source / '.claude-plugin')
        shutil.copytree(ROOT / 'packaging', self.source / 'packaging')
        for product in ROOT.glob('*/.claude-plugin'):
            shutil.copytree(product, self.source / product.relative_to(ROOT))
        self.destination = self.base / 'project with spaces' / '.agents' / 'skills'

    def run_install(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return install(self.source, self.destination, **kwargs)

    def test_all_skills_validate(self):
        skills, errors = validate(self.source)
        self.assertEqual(8, len(skills))
        self.assertEqual([], errors)

    def test_install_every_complete_skill(self):
        self.run_install()
        for name, source in discover(self.source).items():
            target = self.destination / name
            self.assertEqual(fingerprint(source), fingerprint(target))
            self.assertEqual([], validate_skill(target))
            self.assertTrue((target / STAMP).is_file())

    def test_repeating_install_is_unchanged(self):
        self.run_install()
        before = {p: p.stat().st_mtime_ns for p in self.destination.rglob('*') if p.is_file()}
        plan = self.run_install()
        self.assertTrue(all(action == 'unchanged' for action, *_ in plan))
        self.assertEqual(before, {p: p.stat().st_mtime_ns for p in before})

    def test_select_one_skill(self):
        self.run_install(names=['revit-connector'])
        self.assertEqual(['revit-connector'], sorted(p.name for p in self.destination.iterdir()))

    def test_dry_run_does_not_create_destination(self):
        plan = self.run_install(dry_run=True)
        self.assertEqual(8, len(plan))
        self.assertFalse(self.destination.exists())

    def test_unknown_name_writes_nothing(self):
        with self.assertRaises(ValueError):
            self.run_install(names=['missing-connector'])
        self.assertFalse(self.destination.exists())

    def test_collision_preflights_all_targets(self):
        existing = self.destination / 'unreal-connector'
        existing.mkdir(parents=True)
        (existing / 'notes.txt').write_text('User work', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.run_install()
        self.assertEqual(['unreal-connector'], sorted(p.name for p in self.destination.iterdir()))
        self.assertEqual('User work', (existing / 'notes.txt').read_text())

    def test_update_preserves_old_payload_as_zip(self):
        self.run_install(names=['revit-connector'])
        old = fingerprint(self.destination / 'revit-connector')
        source = discover(self.source)['revit-connector']
        with (source / 'SKILL.md').open('a', encoding='utf-8') as f:
            f.write('\nUpdated operating guidance.\n')
        self.run_install(names=['revit-connector'], update=True)
        self.assertEqual(fingerprint(source), fingerprint(self.destination / 'revit-connector'))
        backups = list((self.destination / '.connector-backups').glob('*.zip'))
        self.assertEqual(1, len(backups))
        with ZipFile(backups[0]) as archive:
            archive.extractall(self.base / 'restored')
        self.assertEqual(old, fingerprint(self.base / 'restored' / 'revit-connector'))
        self.assertFalse(list((self.destination / '.connector-backups').rglob('SKILL.md')))

    def test_update_refuses_modified_installed_skill(self):
        self.run_install(names=['revit-connector'])
        target = self.destination / 'revit-connector' / 'SKILL.md'
        target.write_text(target.read_text() + '\nUser customisation.\n', encoding='utf-8')
        before = target.read_bytes()
        with self.assertRaises(ValueError):
            self.run_install(names=['revit-connector'], update=True)
        self.assertEqual(before, target.read_bytes())

    def test_update_refuses_unmanaged_skill(self):
        self.run_install(names=['revit-connector'])
        target = self.destination / 'revit-connector'
        (target / STAMP).unlink()
        (target / 'notes.txt').write_text('Custom work', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.run_install(names=['revit-connector'], update=True)
        self.assertTrue((target / 'notes.txt').exists())

    def test_symlink_destination_is_not_overwritten(self):
        self.destination.mkdir(parents=True)
        outside = self.base / 'outside'
        outside.mkdir()
        try:
            (self.destination / 'revit-connector').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('Creating symlinks is unavailable on this runner')
        with self.assertRaises(ValueError):
            self.run_install(names=['revit-connector'], update=True)
        self.assertEqual([], list(outside.iterdir()))

    def test_missing_reference_fails_validation(self):
        folder = discover(self.source)['revit-connector']
        reference = folder / 'references' / 'example.md'
        reference.parent.mkdir()
        reference.write_text('A connector usage example.\n', encoding='utf-8')
        with (folder / 'SKILL.md').open('a', encoding='utf-8') as f:
            f.write('\n[Usage example](references/example.md)\n')
        self.assertEqual([], validate_skill(folder))
        reference.unlink()
        self.assertTrue(validate_skill(folder))

    def test_cross_skill_reference_is_not_portable(self):
        folder = discover(self.source)['revit-connector']
        with (folder / 'SKILL.md').open('a', encoding='utf-8') as f:
            f.write('\n[External dependency](../../../autocad/skills/autocad-connector/SKILL.md)\n')
        self.assertTrue(validate_skill(folder))

    def test_non_mapping_metadata_fails_cleanly(self):
        folder = discover(self.source)['revit-connector']
        (folder / 'agents' / 'openai.yaml').write_text('[]\n', encoding='utf-8')
        self.assertTrue(validate_skill(folder))

    def test_empty_frontmatter_fails(self):
        folder = discover(self.source)['revit-connector']
        (folder / 'SKILL.md').write_text('---\nname: ""\ndescription: ""\n---\nBody\n', encoding='utf-8')
        self.assertTrue(validate_skill(folder))

    def test_archives_are_independently_usable(self):
        archives = package(self.source, self.base / 'zip output')
        self.assertEqual(8, len(archives))
        skills = discover(self.source)
        for path in archives:
            isolated = self.base / 'unpacked' / path.stem
            with ZipFile(path) as archive:
                self.assertTrue(all(name.startswith(path.stem + '/') for name in archive.namelist()))
                archive.extractall(isolated)
            unpacked = isolated / path.stem
            self.assertEqual(fingerprint(skills[path.stem]), fingerprint(unpacked))
            self.assertEqual([], validate_skill(unpacked))

    def add_private_skill(self):
        folder = self.source / 'private-workflow' / 'skills' / 'private-workflow'
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text('PRIVATE WORKFLOW SENTINEL', encoding='utf-8')
        return folder

    def test_unlisted_private_skill_is_neither_installed_nor_packaged(self):
        self.add_private_skill()
        self.assertNotIn('private-workflow', discover(self.source))
        self.run_install()
        self.assertFalse((self.destination / 'private-workflow').exists())
        with self.assertRaises(ValueError):
            self.run_install(names=['private-workflow'])
        archives = package(self.source, self.base / 'public zips')
        self.assertEqual(8, len(archives))
        for path in archives:
            with ZipFile(path) as archive:
                self.assertTrue(all(b'PRIVATE WORKFLOW SENTINEL' not in archive.read(name)
                                    for name in archive.namelist()))

    def test_stale_archive_is_rejected_without_mixing_packages(self):
        output = self.base / 'stale output'
        output.mkdir()
        stale = output / 'private-workflow.zip'
        stale.write_bytes(b'Private artifact')
        with self.assertRaises(ValueError):
            package(self.source, output)
        with self.assertRaises(ValueError):
            package_plugin(self.source, output)
        self.assertEqual([stale], list(output.iterdir()))
        self.assertEqual(b'Private artifact', stale.read_bytes())

    def test_extra_material_blocks_distribution_before_writing(self):
        folder = discover(self.source)['revit-connector']
        for relative in ['references/example.md', 'notes.md', 'assets/reference.pdf']:
            with self.subTest(path=relative):
                extra = folder / relative
                extra.parent.mkdir(parents=True, exist_ok=True)
                extra.write_bytes(b'PRIVATE REFERENCE SENTINEL')
                with self.assertRaisesRegex(ValueError, 'Extra files in public skill'):
                    validate(self.source)
                with self.assertRaisesRegex(ValueError, 'Extra files in public skill'):
                    self.run_install()
                for builder in [package, package_plugin]:
                    output = self.base / builder.__name__
                    with self.assertRaisesRegex(ValueError, 'Extra files in public skill'):
                        builder(self.source, output)
                    self.assertFalse(output.exists())
                self.assertFalse(self.destination.exists())
                self.assertEqual(b'PRIVATE REFERENCE SENTINEL', extra.read_bytes())
                extra.unlink()

    def test_public_inventory_rejects_external_paths_and_duplicates(self):
        path = self.source / '.claude-plugin' / 'marketplace.json'
        original = json.loads(path.read_text())
        for source in ['../outside', '/tmp/outside', './revit/../../outside']:
            data = json.loads(json.dumps(original))
            data['plugins'][0]['source'] = source
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                discover(self.source)
        original['plugins'].append(original['plugins'][0])
        path.write_text(json.dumps(original), encoding='utf-8')
        with self.assertRaises(ValueError):
            discover(self.source)

    def test_plugin_payload_matches_public_skill_sources(self):
        self.add_private_skill()
        folder, path = package_plugin(self.source, self.base / 'plugin output')
        public = discover(self.source)
        self.assertEqual(set(public), {p.name for p in (folder / 'skills').iterdir()})
        for name, source in public.items():
            self.assertEqual(fingerprint(source), fingerprint(folder / 'skills' / name))
            self.assertEqual([], validate_skill(folder / 'skills' / name))
        portable = json.loads((folder / 'plugin.json').read_text())
        for relative in ['.codex-plugin/plugin.json', '.claude-plugin/plugin.json']:
            manifest = json.loads((folder / relative).read_text())
            self.assertEqual(portable['name'], manifest['name'])
            self.assertEqual(portable['version'], manifest['version'])
            self.assertEqual('AUTOM8LABS', manifest['author']['name'])
            self.assertEqual('./skills/', manifest['skills'])
            self.assertNotIn('license', manifest)
            self.assertNotIn('mcpServers', manifest)
            self.assertNotIn('apps', manifest)
        with ZipFile(path) as archive:
            self.assertEqual({f'{folder.name}/{name}' for name in fingerprint(folder)},
                             set(archive.namelist()))
            archive.extractall(self.base / 'plugin unpacked')
        self.assertEqual(fingerprint(folder), fingerprint(self.base / 'plugin unpacked' / folder.name))

    def test_plugin_refuses_output_inside_a_skill(self):
        source = discover(self.source)['revit-connector']
        before = fingerprint(source)
        with self.assertRaises(ValueError):
            package_plugin(self.source, source / 'generated')
        self.assertEqual(before, fingerprint(source))


if __name__ == '__main__':
    unittest.main()
