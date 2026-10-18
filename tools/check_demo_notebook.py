"""Execute only the small maintained notebook, never the historical experiments."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
notebook = json.loads((root/'notebooks/transport_demo.ipynb').read_text(encoding='utf-8'))
namespace = {'__name__': '__main__'}
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        exec(compile(''.join(cell['source']), '<transport_demo>', 'exec'), namespace)
print('Maintained notebook executed successfully.')
