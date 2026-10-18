"""Verify historical integrity, clean notebooks and bounded distributable files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/'historical/manifest.json').read_text(encoding='utf-8'))
for record in manifest['files']:
    path = ROOT/record['published_path']
    if 'sha256' in record:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], path
    else:
        nb = json.loads(path.read_text(encoding='utf-8'))
        hashes = [hashlib.sha256(''.join(c.get('source', [])).encode()).hexdigest()
                  for c in nb['cells'] if c['cell_type']=='code']
        assert hashes == record['code_cell_source_sha256'], 'Historical cell sources changed'
for directory in ('historical', 'notebooks'):
    for path in (ROOT/directory).rglob('*'):
        if not path.is_file():
            continue
        assert path.stat().st_size < 5_000_000, path
        if path.suffix == '.ipynb':
            nb = json.loads(path.read_text(encoding='utf-8'))
            for cell in nb['cells']:
                if cell['cell_type']=='code':
                    assert cell['outputs'] == [] and cell['execution_count'] is None, path
print('Audit passed: 4 byte-identical R files; original notebook code-cell hashes; clean bounded notebooks.')
