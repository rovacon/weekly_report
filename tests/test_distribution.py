"""Exercise installation and updates with isolated local Git remotes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = 'https://github.com/rovacon/weekly_report.git'


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='weekly report test ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=str(self.base / 'gitconfig'),
                        GIT_TERMINAL_PROMPT='0')
        self.env.update(GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.invalid',
                        GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.invalid')
        self.origin = self.base / 'origin.git'
        self.source = self.base / 'publisher'
        self.checkout = self.base / 'employee checkout'
        self.run_cmd('git', 'init', '--bare', '--initial-branch=main', str(self.origin))
        self.run_cmd('git', 'init', '--initial-branch=main', str(self.source))
        shutil.copytree(ROOT / 'skills', self.source / 'skills')
        shutil.copytree(ROOT / 'scripts', self.source / 'scripts')
        self.commit(self.source, 'Initial')
        self.run_cmd('git', '-C', str(self.source), 'remote', 'add', 'origin', str(self.origin))
        self.run_cmd('git', '-C', str(self.source), 'push', 'origin', 'main')
        self.run_cmd('git', 'clone', str(self.origin), str(self.checkout))
        self.run_cmd('git', '-C', str(self.checkout), 'remote', 'set-url', 'origin', OFFICIAL)
        self.run_cmd('git', '-C', str(self.checkout), 'config',
                     f'url.{self.origin}.insteadOf', OFFICIAL)
        self.target = self.base / 'agent skills'

    def run_cmd(self, *args, ok=True):
        result = subprocess.run(args, env=self.env, text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def commit(self, directory, message):
        self.run_cmd('git', '-C', str(directory), 'add', '.')
        self.run_cmd('git', '-C', str(directory), 'commit', '-m', message)

    def install(self, ok=True):
        return self.run_cmd('bash', str(self.checkout / 'scripts/install.sh'),
                            '--target', str(self.target), ok=ok)

    def update(self, ok=True, linked=False):
        skill = self.target / 'orderpin-weekly-report' if linked else self.checkout / 'skills/orderpin-weekly-report'
        return self.run_cmd('bash', str(skill / 'scripts/update.sh'), ok=ok)

    def test_install_is_idempotent(self):
        self.install()
        self.install()
        self.assertEqual((self.target / 'orderpin-weekly-report').resolve(),
                         self.checkout / 'skills/orderpin-weekly-report')

    def test_existing_skill_preserved(self):
        existing = self.target / 'orderpin-weekly-report'
        existing.mkdir(parents=True)
        (existing / 'personal.txt').write_text('keep')
        self.install(ok=False)
        self.assertEqual((existing / 'personal.txt').read_text(), 'keep')

    def test_update_through_link_gets_new_rules(self):
        self.install()
        rules = self.source / 'skills/orderpin-weekly-report/SKILL.md'
        rules.write_text(rules.read_text() + '\nNew rule\n')
        self.commit(self.source, 'Update rule')
        self.run_cmd('git', '-C', str(self.source), 'push', 'origin', 'main')
        self.update(linked=True)
        self.assertIn('New rule', (self.target / 'orderpin-weekly-report/SKILL.md').read_text())

    def test_dirty_checkout_preserved(self):
        rules = self.checkout / 'skills/orderpin-weekly-report/SKILL.md'
        rules.write_text('personal change')
        self.update(ok=False)
        self.assertEqual(rules.read_text(), 'personal change')

    def test_local_commit_not_treated_as_current(self):
        (self.checkout / 'extra.txt').write_text('local work')
        self.commit(self.checkout, 'Local only')
        self.update(ok=False)
        self.assertTrue((self.checkout / 'extra.txt').exists())

    def test_wrong_branch_stops(self):
        self.run_cmd('git', '-C', str(self.checkout), 'switch', '-c', 'personal')
        self.update(ok=False)

    def test_wrong_remote_stops(self):
        self.run_cmd('git', '-C', str(self.checkout), 'remote', 'set-url', 'origin', str(self.origin))
        self.update(ok=False)

    def test_unavailable_remote_stops(self):
        self.run_cmd('git', '-C', str(self.checkout), 'config',
                     f'url.{self.origin}.insteadOf', 'unused')
        self.run_cmd('git', '-C', str(self.checkout), 'config',
                     f'url.{self.base / "missing.git"}.insteadOf', OFFICIAL)
        self.update(ok=False)


if __name__ == '__main__':
    unittest.main()
