#!/usr/bin/env python3
"""Run both getting-started paths with installed binaries, outside a checkout."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

FIXTURES = Path(__file__).resolve().parent / 'fixtures'
LAW = str(Path(sys.argv[1]).resolve())
with tempfile.TemporaryDirectory(prefix='arxo-release-quickstarts-') as tmp:
    root = Path(tmp)
    def run(*args, cwd=None):
        result = subprocess.run([LAW, *map(str, args)], cwd=cwd or root,
                                capture_output=True, text=True, timeout=120)
        print('$ law ' + ' '.join(map(str, args)), flush=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return result.stdout
    run('init', 'personal', '--name', 'personal.firstcase', '--template', 'case')
    personal = root / 'personal'
    (personal / 'main.lawcase').write_text('''language "law.core" version "0.2";
case Main {
    context {
        legal_time @2026-09-08;
        knowledge_time @2026-09-08T12:00:00+03:00;
        decision_time @2026-09-08T12:00:00+03:00;
        timezone "Europe/Moscow";
    }
}
''')
    run('engine', 'check', '.', cwd=personal)
    run('engine', 'resolve', '.', '--json', cwd=personal)
    run('ask', '--query', 'evaluate positions();', '--query-id', 'first', '--out', 'runs/first', cwd=personal)
    run('eval', 'runs/first', cwd=personal)
    # The guide asks the reader to choose an available canon; use the repaired public release.
    run('add', 'ru.dal.poslovitsy@0.2.3', '--dry-run', cwd=personal)
    run('add', 'ru.dal.poslovitsy@0.2.3', cwd=personal)
    run('install', '--offline', cwd=personal)
    run('engine', 'lock', '.', '--check', cwd=personal)
    run('init', 'parcel-tariff', '--name', 'demo.parcel_tariff', '--template', 'package')
    package = root / 'parcel-tariff'
    (package / 'source.law').write_bytes((FIXTURES / 'parcel-tariff/source.law').read_bytes())
    (package / 'tests').mkdir(exist_ok=True)
    (package / 'tests/tariff.lawtest').write_bytes((FIXTURES / 'parcel-tariff/tests/tariff.lawtest').read_bytes())
    with (package / 'law.toml').open('ab') as out:
        out.write((FIXTURES / 'parcel-tariff/law.toml.append.toml').read_bytes())
    run('engine', 'check', '.', cwd=package)
    run('engine', 'lock', '.', '--write', cwd=package)
    tests = json.loads(run('test', '--json', cwd=package))
    assert tests['passed'] == tests['total'] == 2 and tests['failed'] == 0, tests
    run('pack', '--project', package, '--out', root / 'artifact')
    run('publish', root / 'artifact', '--registry', 'demo=' + str(root / 'registry'))
    run('init', 'consumer', '--name', 'demo.consumer', '--template', 'case')
    run('add', 'demo.parcel_tariff@0.1.0', '--project', root / 'consumer', '--from', 'demo',
        '--registry', 'demo=' + str(root / 'registry'))
    run('install', '--project', root / 'consumer', '--offline')
    run('engine', 'lock', root / 'consumer', '--check', '--registry', root / 'registry')
print('PASS: personal case, saved replay, public canon installation, tariff tests and local publication')
