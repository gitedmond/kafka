"""Run the exact original/fixed CLI scripts, locally or against this fork PR."""
import argparse
import difflib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--local', action='store_true')
args = parser.parse_args()
out = Path('demo-results').resolve()
out.mkdir(exist_ok=True)
source = (ROOT / 'input.md').read_text()
env = os.environ.copy()
env['GITHUB_ACTIONS'] = 'true'
env.setdefault('PR_NUMBER', '1')

def gh(*arguments):
    return subprocess.check_output(['gh', *arguments], env=env, text=True)

def body():
    return json.loads(gh('pr', 'view', env['PR_NUMBER'], '--json', 'body'))['body']

def restore():
    gh('pr', 'edit', env['PR_NUMBER'], '--body-file', str(ROOT / 'input.md'))

def run(stage, script):
    result = subprocess.run([sys.executable, str(ROOT / script)], env=env,
                            capture_output=True, text=True)
    (out / (stage + '.log')).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(stage + ' failed; see captured log')
    current = body()
    (out / (stage + '.md')).write_text(current)
    return current, result.stderr

stub = '''#!/usr/bin/env python3
import json, os, pathlib, sys
state = pathlib.Path(os.environ['DEMO_STATE'])
data = json.loads(state.read_text())
if sys.argv[1:3] == ['pr', 'view']:
    print(json.dumps(data))
elif sys.argv[1:3] == ['pr', 'edit']:
    data['body'] = pathlib.Path(sys.argv[sys.argv.index('--body-file')+1]).read_text()
    data['edits'] += 1
    state.write_text(json.dumps(data))
else:
    raise SystemExit('Unexpected gh invocation')
'''

with tempfile.TemporaryDirectory() as temp:
    if args.local:
        fake = Path(temp) / 'gh'
        fake.write_text(stub)
        fake.chmod(0o755)
        state = Path(temp) / 'state.json'
        state.write_text(json.dumps({'title': 'KAFKA-21205 Markdown demonstration',
                                     'body': source, 'reviews': [], 'edits': 0}))
        env['DEMO_STATE'] = str(state)
        env['PATH'] = temp + os.pathsep + env['PATH']
    else:
        # Limit writes to this explicitly named, same-repository demonstration.
        if env.get('GH_REPO') != 'gitedmond/kafka':
            raise RuntimeError('Live demo must target gitedmond/kafka')
        metadata = json.loads(gh('pr', 'view', env['PR_NUMBER'], '--json',
                                 'headRefName,headRepositoryOwner,isCrossRepository'))
        if (metadata['headRefName'] != 'demo/kafka-21205-markdown'
                or metadata['headRepositoryOwner']['login'] != 'gitedmond'
                or metadata['isCrossRepository']):
            raise RuntimeError('Unexpected PR; refusing description writes')
    try:
        restore()
        (out / 'input.md').write_text(body())
        assert body() == source, 'Input must be restored exactly'
        old, _ = run('before', 'old-pr-format.py')
        assert 'Example list:  - first item  - second item' in old
        assert '    second = 2\n    return first + second' not in old
        assert '    result = call_with_many_arguments(first_argument, second_argument, third_argument, fourth_argument, fifth_argument)' not in old
        restore()
        after, first_log = run('after', 'fixed-pr-format.py')
        again, second_log = run('after-again', 'fixed-pr-format.py')
        assert after == source, 'Fixed formatter changed the structured input'
        assert again == after, 'Fixed formatter is not idempotent'
        assert 'body is already formatted.' in first_log
        assert 'body is already formatted.' in second_log
        if args.local:
            # Two explicit restores plus one old-script write; neither fixed run writes.
            assert json.loads(state.read_text())['edits'] == 3
        (out / 'before.diff').write_text(''.join(difflib.unified_diff(
            source.splitlines(True), old.splitlines(True), fromfile='input.md', tofile='before.md')))
        summary = ('# KAFKA-21205 demonstration results\n\n'
                   + ('Mode: local CLI simulation (GitHub reads/writes substituted).\n\n' if args.local
                      else 'Mode: live GitHub PR description reads/writes.\n\n')
                   + '| Check | Original | Fixed |\n| --- | --- | --- |\n'
                   + '| Indented list | Collapses into one line | Preserved |\n'
                   + '| Code after blank line | Lines joined / indentation lost | Preserved |\n'
                   + '| Long indented code line | Wrapped / indentation lost | Preserved |\n'
                   + '| Full description equals input | No | Yes |\n'
                   + '| Second fixed run | — | Unchanged; no write needed |\n\n'
                   + 'Both exact CLI scripts exited successfully. The original passes its\n'
                   + 'lint checks while corrupting the Markdown. The fixed version preserves\n'
                   + 'the entire input and logs that no rewrite is necessary on both runs.\n')
        (out / 'summary.md').write_text(summary)
        print(summary)
        if env.get('GITHUB_STEP_SUMMARY'):
            with open(env['GITHUB_STEP_SUMMARY'], 'a') as handle:
                handle.write(summary)
    finally:
        # Never leave the demonstration description corrupted if a check fails.
        if not args.local and body() != source:
            restore()
