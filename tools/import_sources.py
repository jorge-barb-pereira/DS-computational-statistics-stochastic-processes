"""Import explicitly selected historical sources without executing them.

Usage: python tools/import_sources.py "path/to/original/course/folder"
The input folder is read only. Existing curated files are replaced deterministically.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    source = parser.parse_args().source.resolve(strict=True)
    manifest = {'imported_on': '2026-10-18', 'files': []}
    for name in ('Script.R', 'Script (1).R', 'Script 4 .R', 'Script_Final.R'):
        original = source/'Projeto'/name
        destination = ROOT/'historical/r'/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, destination)
        manifest['files'].append({
            'original_path': original.relative_to(source).as_posix(),
            'published_path': destination.relative_to(ROOT).as_posix(),
            'sha256': sha(original.read_bytes()), 'transformation': 'verbatim byte copy',
            'filesystem_modified_utc': datetime.fromtimestamp(original.stat().st_mtime, timezone.utc).isoformat(),
        })
    original = source/'PEA/MC-PS.ipynb'
    data = original.read_bytes()
    notebook = json.loads(data)
    code_hashes = [sha(''.join(c.get('source', [])).encode()) for c in notebook['cells'] if c['cell_type']=='code']
    for i, cell in enumerate(notebook['cells']):
        cell['id'] = f'historical-{i:03d}'
        cell['metadata'] = {}
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    notebook['cells'].insert(0, {'cell_type': 'markdown', 'id': 'historical-warning', 'metadata': {}, 'source': [
        '# Historical photon-transport experiments\n',
        'Original code cells retained for provenance; outputs and execution metadata removed.\n',
        '**Some cells require substantial runtime and memory and contain known model defects.**\n',
        'Use `notebooks/transport_demo.ipynb` for the maintained, bounded example.\n',
        'See `docs/REVIEW.md` before running historical experiments.\n',
    ]})
    notebook['metadata'] = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}}
    notebook['nbformat'] = 4
    notebook['nbformat_minor'] = 5
    destination = ROOT/'historical/python/MC-PS.ipynb'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(notebook, indent=1, ensure_ascii=False)+'\n', encoding='utf-8')
    manifest['files'].append({
        'original_path': 'PEA/MC-PS.ipynb', 'published_path': destination.relative_to(ROOT).as_posix(),
        'original_sha256': sha(data), 'original_bytes': len(data),
        'code_cell_source_sha256': code_hashes,
        'filesystem_modified_utc': datetime.fromtimestamp(original.stat().st_mtime, timezone.utc).isoformat(),
        'development_date': 'Unknown; filesystem timestamp alone is not proof of authorship date',
        'transformation': 'Code sources unchanged; outputs and execution metadata removed; warning added',
    })
    (ROOT/'historical/manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(f'Imported 4 R sources and {len(code_hashes)} notebook code cells without execution.')


if __name__ == '__main__':
    main()
