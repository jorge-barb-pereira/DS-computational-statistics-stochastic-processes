"""Generate small reproducible Monte Carlo transport examples."""
import argparse
import json
from pathlib import Path
import numpy as np
from .transport import MATERIALS, simulate_ensemble


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--histories', type=int, default=4)
    parser.add_argument('--photons', type=int, default=300)
    parser.add_argument('--grid-size', type=int, default=24)
    parser.add_argument('--length', type=float, default=10)
    parser.add_argument('--material', choices=MATERIALS, default='legacy-lead')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, default=Path('output/python'))
    args = parser.parse_args()
    try:
        result = simulate_ensemble(args.histories, args.photons, args.seed,
                                   grid_size=args.grid_size, length=args.length, material=args.material)
    except (ValueError, RuntimeError) as exc:
        parser.exit(2, f'Error: {exc}\n')
    args.output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output/'transport.npz', mean=result['mean_mev_per_primary'],
                         sem=result['sem_mev_per_primary'])
    metrics = {k:v for k,v in result.items() if k not in ('mean_mev_per_primary','sem_mev_per_primary')}
    metrics['material'] = args.material
    metrics['mean_deposited_mev_per_primary'] = float(result['mean_mev_per_primary'].sum())
    (args.output/'summary.json').write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    from .plotting import plot_transport
    plot_transport(result,args.length,args.output/'transport.png')
    print(f"Saved {args.histories} batches of {args.photons} primaries to {args.output}")
    print(f"Mean deposited energy: {metrics['mean_deposited_mev_per_primary']:.6f} MeV per primary")
