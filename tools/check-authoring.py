#!/usr/bin/env python3
"""Focused offline fixtures for staged authoring and bounded publication evidence."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import importlib.machinery
import importlib.util
import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


check = load('article_check', ROOT / 'bin/check-articles')
observe = load('publication_observer', ROOT / 'bin/observe-publication')
audit = load('import_audit', ROOT / 'tools/import-wordpress-check')


class Articles(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'content/posts').mkdir(parents=True)
        for source in (ROOT / 'content/posts').rglob('index.*.*'):
            target = self.root / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        shutil.copytree(ROOT / 'data', self.root / 'data')
        (self.root / 'tools').mkdir()
        for name in ('import-wordpress', 'import-wordpress-check', 'spelling-cs.txt', 'spelling-en.txt'):
            shutil.copy2(ROOT / 'tools' / name, self.root / 'tools' / name)
        self.git('init', '--quiet')
        self.git('add', '.')
        message = self.root / 'message'
        message.write_text('Create isolated authoring fixture\n')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '--quiet', '-F', str(message))
        message.unlink()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.PIPE)

    def pair(self, cs='Nový článek', english='New article', draft=False, first='cs', code=False):
        self.cs = self.root / 'content/posts/2026-11-09-new-article/index.cs.md'
        self.en = self.cs.with_name('index.en.md')
        self.cs.parent.mkdir(parents=True, exist_ok=True)
        def source(language, title, body):
            path = '/novy-clanek/' if language == 'cs' else '/new-article/'
            return f'+++\ntitle = {json.dumps(title, ensure_ascii=False)}\ndate = "2026-11-09T10:00:00+01:00"\nlastmod = "2026-11-09T10:00:00+01:00"\ndraft = {str(draft).lower()}\nurl = "{path}"\ntranslationKey = "post-fixture"\ncategories = ["technologie"]\n[params]\narticle_id = "post-fixture"\n' + ('+++\n'+body if language == 'cs' else 'translation_status = "reviewed"\ntranslation_reviewed_by = "fixture-agent"\ntranslation_reviewed_at = "2026-11-09T11:00:00+01:00"\ntranslation_source_sha256 = "SOURCE"\n+++\n'+body)
        cs_body = 'Nový článek o systému Linux.\n'
        en_body = 'New article about Linux.\n'
        if code:
            en_body += '\n`mispeledidentifier` [valid link](https://example.invalid/mispeledurl)\n\n```sh\nverybadcodewordzz\n```\n'
        content = {'cs': source('cs', cs, cs_body), 'en': source('en', english, en_body)}
        for language in (first, 'en' if first == 'cs' else 'cs'):
            (self.cs if language == 'cs' else self.en).write_text(content[language])
        self.bind()
        data_path = self.root / 'data/articles.json'
        data = json.loads(data_path.read_bytes())
        data['post-fixture'] = {'author_ids': ['wp-user-6'], 'discussion_url': 'https://blog.vpsfree.cz/novy-clanek/', 'feed_guids': {language: f'urn:vpsfree:blog:post-fixture:{language}' for language in ('cs', 'en')}}
        data_path.write_bytes(audit.wp.encoded(data))

    def bind(self):
        raw = self.en.read_text()
        import re
        digest = hashlib.sha256(self.cs.read_bytes()).hexdigest()
        self.en.write_text(re.sub(r'translation_source_sha256 = "[^"]*"', f'translation_source_sha256 = "{digest}"', raw))

    def validate(self, staged=False):
        return check.check(check.Source(self.root, staged))

    def test_cs_first_and_en_first_pairs_with_code(self):
        for first in ('cs', 'en'):
            self.pair(first=first, code=True)
            self.validate()

    def test_index_bad_working_fixed_and_index_good_working_bad(self):
        self.pair(cs='Spatnslovozzz článek')
        self.git('add', '.')
        self.cs.write_text(self.cs.read_text().replace('Spatnslovozzz', 'Nový'))
        self.bind()
        with self.assertRaisesRegex(check.Invalid, 'unknown prose/title words'):
            self.validate(staged=True)
        self.git('add', '.')
        self.cs.write_text(self.cs.read_text().replace('Nový', 'Spatnslovozzz'))
        self.validate(staged=True)

    def test_real_precommit_hook_blocks_index_and_preserves_unstaged_changes(self):
        self.pair(cs='Spatnslovozzz článek')
        (self.root / 'bin').mkdir()
        shutil.copy2(ROOT / 'bin/check-articles', self.root / 'bin/check-articles')
        shutil.copytree(ROOT / '.githooks', self.root / '.githooks')
        for name in ('flake.nix', 'flake.lock'):
            shutil.copy2(ROOT / name, self.root / name)
        self.git('add', '.')
        self.git('config', '--local', 'core.hooksPath', '.githooks')
        message = self.root / 'message'
        message.write_text('Commit isolated bilingual fixture\n')
        command = ['git', '-C', str(self.root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-F', str(message)]
        bad = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn(b'unknown prose/title words', bad.stderr)
        self.cs.write_text(self.cs.read_text().replace('Spatnslovozzz', 'Nový'))
        self.bind()
        self.git('add', self.cs.relative_to(self.root).as_posix(), self.en.relative_to(self.root).as_posix())
        self.cs.write_text(self.cs.read_text().replace('Nový', 'Spatnslovozzz'))
        good = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(good.returncode, 0, good.stderr.decode())
        self.assertIn('Spatnslovozzz', self.cs.read_text())
        self.assertIn('Nový'.encode(), self.git('show', 'HEAD:' + self.cs.relative_to(self.root).as_posix()))

    def test_missing_language_even_for_draft_and_stale_hash(self):
        self.pair(draft=True)
        self.en.unlink()
        with self.assertRaisesRegex(check.Invalid, 'both CS and EN'):
            self.validate()
        self.pair(draft=True)
        self.cs.write_text(self.cs.read_text().replace('Nový', 'Další'))
        with self.assertRaisesRegex(check.Invalid, 'stale translation_source'):
            self.validate()

    def test_metadata_failures_and_duplicate_identity(self):
        self.pair()
        valid = self.cs.read_text()
        for before, after in [('title = "Nový článek"', 'title = ""'), ('title = "Nový článek"', 'title = ['), ('draft = false', 'draft = "false"'), ('2026-11-09T10:00:00+01:00', '2026-11-09T10:00:00'), ('translationKey = "post-fixture"', 'translationKey = "other"')]:
            self.cs.write_text(valid.replace(before, after))
            self.bind()
            with self.subTest(field=before), self.assertRaises(check.Invalid):
                self.validate()
        self.cs.write_text(valid)
        self.bind()
        duplicate = self.cs.with_suffix('.html')
        duplicate.write_bytes(self.cs.read_bytes())
        with self.assertRaisesRegex(check.Invalid, 'duplicate'):
            self.validate()

    def test_staged_companion_delete_and_bundle_rename(self):
        self.pair(draft=True)
        self.git('add', '.')
        self.git('rm', '--cached', self.en.relative_to(self.root).as_posix())
        with self.assertRaisesRegex(check.Invalid, 'both CS and EN'):
            self.validate(staged=True)
        self.git('add', '.')
        self.validate(staged=True)
        self.git('mv', self.en.relative_to(self.root).as_posix(), 'content/posts/2026-11-09-new-article/index.en.html')
        self.validate(staged=True)

    def test_new_czech_slug_excludes_numeric_and_wp_roots(self):
        self.pair()
        self.validate()
        original = self.cs.read_text()
        path = self.root / 'data/articles.json'
        data = json.loads(path.read_text())
        for url in ('/123/', '/wp-example/'):
            self.cs.write_text(original.replace('/novy-clanek/', url))
            self.bind()
            data['post-fixture']['discussion_url'] = 'https://blog.vpsfree.cz' + url
            path.write_bytes(audit.wp.encoded(data))
            with self.subTest(url=url), self.assertRaisesRegex(check.Invalid, 'new Czech URL'):
                self.validate()

    def test_shared_original_projection_additions_and_tampering(self):
        self.pair()
        self.validate()
        manifest = json.loads((self.root / 'data/migration/source-manifest.json').read_bytes())
        for name in ('articles', 'authors', 'taxonomies'):
            path = self.root / f'data/{name}.json'
            original = json.loads(path.read_bytes())
            extended = copy.deepcopy(original)
            if name == 'articles':
                extended['post-extra'] = {'public': 'unrelated'}
            elif name == 'authors':
                extended['new-author'] = {'name': 'New Author', 'slug': 'new-author'}
            else:
                extended['tags']['new-tag'] = {'name': 'New tag'}
            digest = hashlib.sha256(audit.original_shared_projection(f'data/{name}.json', extended, manifest)).hexdigest()
            self.assertEqual(digest, manifest['generated_files'][f'data/{name}.json'])
            changed = copy.deepcopy(original)
            if name == 'taxonomies':
                changed['tags']['passkey']['name'] = 'Changed'
            else:
                key = 'wp-8' if name == 'articles' else 'wp-user-6'
                changed[key]['name' if name == 'authors' else 'discussion_url'] = 'Changed'
            self.assertNotEqual(hashlib.sha256(audit.original_shared_projection(f'data/{name}.json', changed, manifest)).hexdigest(), digest)
            if name == 'taxonomies':
                del changed['tags']['passkey']
            else:
                del changed[key]
            with self.assertRaises(AssertionError):
                audit.original_shared_projection(f'data/{name}.json', changed, manifest)

    def test_real_dictionaries_visible_labels_and_legacy_noise(self):
        self.validate()  # Unchanged imported unknown words are not a corpus cleanup.
        self.pair(english='Mispeledzz article')
        with self.assertRaisesRegex(check.Invalid, 'unknown prose/title words'):
            self.validate()
        self.pair(code=True)
        self.validate()
        self.en.write_text(self.en.read_text() + '\n![Mispeledzz](https://example.invalid/image.png)\n')
        with self.assertRaisesRegex(check.Invalid, 'Mispeledzz'):
            self.validate()


class Observer(unittest.TestCase):
    def setUp(self):
        self.sha = 'a' * 40
        self.run = {'id': 1, 'run_number': 9, 'run_attempt': 1, 'head_sha': self.sha, 'head_branch': 'main', 'event': 'push', 'path': observe.WORKFLOW, 'repository': {'full_name': observe.REPOSITORY}, 'status': 'completed', 'conclusion': 'success', 'html_url': 'https://github.com/vpsfreecz/blog/actions/runs/1'}
        self.expected = {lang: {'url': f'https://blog.vpsfree.{host}/example/', 'path': f'{lang}/example/index.html', 'title': 'Example'} for lang, host in [('cs', 'cz'), ('en', 'org')]}
        self.now = 0

    def job_document(self, jobs, attempt=None):
        attempt = self.run['run_attempt'] if attempt is None else attempt
        return {'total_count': len(jobs), 'jobs': [
            {'run_id': self.run['id'], 'head_sha': self.sha, 'run_attempt': attempt, **job}
            for job in jobs]}

    def api(self, path, remaining):
        if '/jobs?' in path:
            return self.job_document([{'name': name, 'status': 'completed', 'conclusion': 'success'} for name in ('build', 'deploy')])
        return {'workflow_runs': [self.run]}

    def page(self, url, remaining):
        return f'<title>Example | vpsFree.cz blog</title><link rel="canonical" href="{url}"><article data-article-id="post-fixture">Body</article>'.encode()

    def sleep(self, seconds):
        self.now += seconds

    def result(self, api=None, fetch=None):
        return observe.observe(self.sha, 'post-fixture', self.expected, 2, 1, api_get=api or self.api, fetch=fetch or self.page, clock=lambda: self.now, sleep=self.sleep)

    def test_exact_run_and_success(self):
        for field, wrong in [('head_sha', 'b'*40), ('head_branch', 'feature'), ('event', 'pull_request'), ('path', 'other.yml')]:
            row = {**self.run, field: wrong}
            self.assertIsNone(observe.exact_run([row], self.sha))
        self.assertEqual(self.result()['ci'], 'success')

    def test_failed_and_skipped_deploy_are_not_success(self):
        for conclusion in ('failure', 'skipped'):
            def api(path, remaining):
                if '/jobs?' in path:
                    return self.job_document([{'name': 'build', 'status': 'completed', 'conclusion': 'success'}, {'name': 'deploy', 'status': 'completed', 'conclusion': conclusion}])
                return {'workflow_runs': [self.run]}
            self.assertEqual(self.result(api)['ci'], 'failed')

    def test_feature_ci_only_without_site_or_draft_preparation(self):
        self.run['head_branch'] = 'article/draft'
        def feature_api(path, remaining):
            if '/jobs?' in path:
                return self.job_document([{'name': 'build', 'status': 'completed', 'conclusion': 'success'}, {'name': 'deploy', 'status': 'completed', 'conclusion': 'skipped'}])
            return {'workflow_runs': [self.run]}
        def no_site(*args):
            self.fail('Feature observation must never request public sites')
        def result(api=feature_api):
            return observe.observe(self.sha, 'draft-id', {}, 2, 1, api_get=api, fetch=no_site, clock=lambda: self.now, sleep=self.sleep, branch='article/draft')
        report = result()
        self.assertEqual(report['ci'], 'success')
        self.assertEqual(report['publication'], 'not requested (draft feature)')
        self.assertEqual(report['site'], {})
        self.assertIsNone(observe.exact_run([{**self.run, 'head_branch': 'other'}], self.sha, 'article/draft'))
        for conclusion in ('failure', 'cancelled'):
            self.run['conclusion'] = conclusion
            self.assertEqual(result()['ci'], 'failed')
        self.run['conclusion'] = 'success'
        def delivered(path, remaining):
            if '/jobs?' in path:
                return self.job_document([{'name': name, 'status': 'completed', 'conclusion': 'success'} for name in ('build', 'deploy')])
            return {'workflow_runs': [self.run]}
        self.assertEqual(result(delivered)['ci'], 'failed')
        def unavailable(*args):
            raise OSError('rate limit')
        self.assertEqual(result(unavailable)['ci'], 'unknown')
        self.now = 0
        self.assertEqual(result(lambda *args: {'workflow_runs': []})['ci'], 'unknown')

    def test_documented_feature_cli_without_article_and_main_requires_article(self):
        command = [str(ROOT / 'bin/observe-publication'), '--sha', self.sha,
                   '--branch', 'article/draft']
        report = {'ci': 'success', 'site': {}, 'publication': 'not requested (draft feature)'}
        with patch('sys.argv', command), patch.object(observe, 'observe', return_value=report) as run, \
                patch.object(observe, 'expected_articles', side_effect=AssertionError('Feature CLI must not prepare public articles')), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(observe.main(), 0)
            self.assertEqual(run.call_args.kwargs['branch'], 'article/draft')
            self.assertEqual(run.call_args.args[2], {})
        error = io.StringIO()
        with patch('sys.argv', command[:3]), patch.object(observe, 'observe') as run, \
                redirect_stderr(error), self.assertRaises(SystemExit) as failure:
            observe.main()
        self.assertEqual(failure.exception.code, 2)
        self.assertIn('--article is required for main', error.getvalue())
        run.assert_not_called()

    def test_deploy_only_rerun_reuses_first_same_run_build(self):
        self.run['run_attempt'] = 2
        build = {'name': 'build', 'status': 'completed', 'conclusion': 'success', 'steps': [
            {'name': 'Package release', 'status': 'completed', 'conclusion': 'success'},
            {'name': 'Run actions/upload-artifact@' + 'a' * 40, 'status': 'completed', 'conclusion': 'success'}]}
        deploy = {'name': 'deploy', 'status': 'completed', 'conclusion': 'success'}
        history = {1: self.job_document([build], 1), 2: self.job_document([deploy], 2)}
        queries = []
        def api(path, remaining):
            if '/jobs?' not in path:
                return {'workflow_runs': [self.run]}
            attempt = int(re.search(r'/attempts/(\d+)/jobs', path)[1])
            queries.append(attempt)
            return history[attempt]
        result = self.result(api)
        self.assertEqual(result['ci'], 'success')
        self.assertEqual((result['build_attempt'], result['deploy_attempt']), (1, 2))
        self.assertEqual(queries, [2, 1])
        for field, wrong in [('run_id', 99), ('head_sha', 'b' * 40), ('run_attempt', 99)]:
            original = history[1]
            history[1] = copy.deepcopy(original)
            history[1]['jobs'][0][field] = wrong
            with self.subTest(field=field):
                self.assertNotEqual(self.result(api)['ci'], 'success')
            history[1] = original
        for field in ('steps',):
            original = history[1]
            history[1] = copy.deepcopy(original)
            del history[1]['jobs'][0][field]
            self.assertNotEqual(self.result(api)['ci'], 'success')
            history[1] = original
        for step in (0, 1):
            original = history[1]
            history[1] = copy.deepcopy(original)
            history[1]['jobs'][0]['steps'][step]['conclusion'] = 'skipped'
            self.assertNotEqual(self.result(api)['ci'], 'success')
            history[1] = original
        for invalid in ({'jobs': []}, {'jobs': [], 'total_count': 1}, self.job_document([], 1)):
            original = history[1]
            history[1] = invalid
            self.assertNotEqual(self.result(api)['ci'], 'success')
            history[1] = original
        self.run['run_attempt'] = 3
        history[3] = self.job_document([deploy], 3)
        for conclusion in ('failure', 'skipped', 'cancelled'):
            history[2] = self.job_document([{**build, 'conclusion': conclusion}], 2)
            queries.clear()
            self.assertNotEqual(self.result(api)['ci'], 'success')
            self.assertEqual(queries, [3, 2])
        history[2] = self.job_document([{**build, 'status': 'in_progress'}], 2)
        self.assertNotEqual(self.result(api)['ci'], 'success')
        history[2] = self.job_document([build, build], 2)
        self.assertNotEqual(self.result(api)['ci'], 'success')

    def test_expected_article_english_underscore_path(self):
        paths = ['content/posts/example/index.cs.md', 'content/posts/example/index.en.md']
        for english_route in ('/new_article/', '/new--article/'):
            raw = []
            for lang, route in [('cs', '/ordinary-cs/'), ('en', english_route)]:
                raw.append(('+++\ntitle="Example"\ndraft=false\nurl="' + route + '"\n[params]\narticle_id="post-fixture"\n+++\nBody').encode())
            with patch.object(observe.subprocess, 'check_output', side_effect=[('\0'.join(paths)+'\0').encode(), *raw]):
                result = observe.expected_articles(self.sha, 'post-fixture')
            self.assertEqual(result['en']['url'], 'https://blog.vpsfree.org' + english_route)
            self.assertEqual(result['cs']['url'], 'https://blog.vpsfree.cz/ordinary-cs/')

    def test_new_attempt_cannot_inherit_earlier_success_while_sites_converge(self):
        def scenario(terminal_third=False, api_failure=False):
            self.now = 0
            polls = 0
            def api(path, remaining):
                nonlocal polls
                if '/jobs?' not in path:
                    polls += 1
                    if api_failure and polls > 1:
                        raise OSError('API unavailable after earlier success')
                    self.run['run_attempt'] = 2 if polls == 1 else 3
                    self.run['status'] = 'completed' if polls == 1 or terminal_third and polls > 2 else 'in_progress'
                    self.run['conclusion'] = 'success' if self.run['status'] == 'completed' else None
                    return {'workflow_runs': [dict(self.run)]}
                status = 'completed' if self.run['status'] == 'completed' else 'in_progress'
                conclusion = 'success' if status == 'completed' else None
                return self.job_document([{'name': name, 'status': status, 'conclusion': conclusion}
                                          for name in ('build', 'deploy')])
            def page(url, remaining):
                if polls == 1 and 'blog.vpsfree.org' in url:
                    return b'Old English page'
                return self.page(url, remaining)
            return observe.observe(self.sha, 'post-fixture', self.expected, 4, 1,
                api_get=api, fetch=page, clock=lambda: self.now, sleep=self.sleep)
        report = scenario()
        self.assertEqual(report['ci'], 'unknown')
        self.assertNotIn('build_attempt', report)
        self.assertNotIn('deploy_attempt', report)
        self.assertNotIn('delivery confirmed', report['publication'])
        with patch('sys.argv', [str(ROOT / 'bin/observe-publication'), '--sha', self.sha,
                                '--article', 'post-fixture']), \
                patch.object(observe, 'expected_articles', return_value=self.expected), \
                patch.object(observe, 'observe', return_value=report), redirect_stdout(io.StringIO()):
            self.assertEqual(observe.main(), 1)
        report = scenario(terminal_third=True)
        self.assertEqual(report['ci'], 'success')
        self.assertEqual((report['build_attempt'], report['deploy_attempt']), (3, 3))
        report = scenario(api_failure=True)
        self.assertEqual(report['ci'], 'unknown')
        self.assertNotIn('build_attempt', report)
        self.assertNotIn('deploy_attempt', report)

    def test_rate_limit_site_only_and_timeout(self):
        def unavailable(*args):
            raise OSError('rate limited')
        result = self.result(unavailable)
        self.assertEqual(result['ci'], 'unknown')
        self.assertIn('unproven', result['publication'])
        self.now = 0
        result = self.result(lambda *args: {'workflow_runs': []}, lambda *args: b'Old page')
        self.assertEqual(result['ci'], 'unknown')
        self.assertTrue(any('timed out' in item for item in result['limits']))


if __name__ == '__main__':
    unittest.main(verbosity=1, failfast=True)
