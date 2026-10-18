"""Reproducible convergence experiments and an absorbing-chain benchmark."""
import argparse
import csv
import json
from pathlib import Path
import platform
from importlib.metadata import version

import numpy as np
from scipy.stats import norm, t

from .markov import slab_chain, sample_slab_chain
from .transport import simulate_batch, positive_integer, MATERIALS


def wilson_interval(successes, trials, level=0.95):
    positive_integer(trials, 'trials')
    if not 0 <= successes <= trials or not 0 < level < 1:
        raise ValueError('Invalid binomial count or confidence level')
    z = float(norm.ppf((1+level)/2))
    p = successes/trials
    denominator = 1+z*z/trials
    center = (p+z*z/(2*trials))/denominator
    half = z*np.sqrt(p*(1-p)/trials+z*z/(4*trials*trials))/denominator
    return max(0.0, center-half), min(1.0, center+half)


def convergence_study(photon_counts=(100, 300, 1000, 3000), replicates=24,
                      seed=20261018, material='legacy-water', grid_size=12):
    """Independent replicates at each N; no high-N run is treated as truth.

    The analytic companion is uncollided slab transmission. Its aggregate
    binomial draws are separate from the 3D transport simulations.
    """
    positive_integer(replicates, 'replicates', 3)
    counts = tuple(photon_counts)
    if len(counts) < 2:
        raise ValueError('At least two increasing photon counts are required')
    for n in counts:
        positive_integer(n, 'photon count', 2)
    if any(b <= a for a, b in zip(counts, counts[1:])):
        raise ValueError('Photon counts must be strictly increasing')
    if material not in MATERIALS:
        raise ValueError('Unknown material')
    children = np.random.SeedSequence(seed).spawn(len(counts)*2)
    rows, all_batches = [], []
    exact_transmission = float(np.exp(-0.771*2.0))
    critical = float(t.ppf(0.975, replicates-1))
    for i, photons in enumerate(counts):
        # Each batch and each photon-count setting gets its own child stream.
        batches = []
        for child in children[2*i].spawn(replicates):
            result = simulate_batch(photons=photons, seed=child, material=material, grid_size=grid_size)
            accounted = result['deposited_mev']+result['escaped_mev']+result['unresolved_mev']
            if not np.isclose(accounted, result['source_mev'], rtol=0, atol=1e-9*photons):
                raise RuntimeError('Transport energy ledger did not balance')
            if result['unresolved_mev'] > 1e-12:
                raise RuntimeError('Convergence study encountered unresolved energy')
            batches.append([result['deposited_mev']/photons, result['escaped_mev']/photons])
        values = np.array(batches)
        all_batches.append(values)
        estimates = np.random.default_rng(children[2*i+1]).binomial(photons, exact_transmission, replicates)/photons
        covered = [wilson_interval(round(x*photons), photons)[0] <= exact_transmission <=
                   wilson_interval(round(x*photons), photons)[1] for x in estimates]
        mean = values.mean(axis=0)
        sd = values.std(axis=0, ddof=1)
        sem = sd/np.sqrt(replicates)
        rows.append({'photons_per_batch': photons, 'replicates': replicates,
                     'total_transport_photons': photons*replicates,
                     'mean_deposited_mev_per_primary': float(mean[0]),
                     'sd_deposited_mev_per_primary': float(sd[0]),
                     'sem_deposited_mev_per_primary': float(sem[0]),
                     'ci95_deposited_lower': float(mean[0]-critical*sem[0]),
                     'ci95_deposited_upper': float(mean[0]+critical*sem[0]),
                     'relative_ci95_half_width': float(critical*sem[0]/mean[0]) if mean[0]>0 else None,
                     'mean_escaped_mev_per_primary': float(mean[1]),
                     'sd_escaped_mev_per_primary': float(sd[1]),
                     'analytic_transmission_probability': exact_transmission,
                     'transmission_rmse': float(np.sqrt(np.mean((estimates-exact_transmission)**2))),
                     'theoretical_transmission_rmse': float(np.sqrt(exact_transmission*(1-exact_transmission)/photons)),
                     'wilson_coverage_fraction': float(np.mean(covered))})
    sd = np.array([r['sd_deposited_mev_per_primary'] for r in rows])
    slope = float(np.polyfit(np.log(counts), np.log(sd), 1)[0]) if np.all(sd>0) else None
    return {'rows': rows, 'batches': all_batches, 'material': material,
            'seed': seed, 'replicates': replicates, 'sd_log_log_slope': slope,
            'grid_size': grid_size, 'ci_method': 'Student t interval across independent batch means; approximate normality'}


def markov_study(photons=50000, seed=20261019):
    chain = slab_chain()
    sample = sample_slab_chain(chain, photons, seed)
    empirical = sample['transmitted']/photons
    interval = wilson_interval(sample['transmitted'], photons, 0.99)
    summary = {'photons': photons, 'seed': seed, 'mu_per_cm': chain['mu'],
               'slab_length_cm': chain['length_cm'], 'bin_width_cm': chain['step_cm'],
               'transient_states': len(chain['edges_cm'])-1,
               'absorbing_states': ['absorbed', 'transmitted'],
               'exact_transmission': float(np.exp(-chain['mu']*chain['length_cm'])),
               'matrix_transmission': float(chain['absorption_probabilities'][0,1]),
               'empirical_transmission': empirical,
               'transmission_ci99_wilson': list(interval),
               'exact_expected_steps': float(chain['expected_steps'][0]),
               'empirical_expected_steps': float(sample['steps_per_path'].mean()),
               'matrix_row_sum_max_error': float(np.max(np.abs(chain['matrix'].sum(axis=1)-1))),
               'absorbed': sample['absorbed'], 'transmitted': sample['transmitted']}
    return {'chain': chain, 'sample': sample, 'summary': summary}


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_studies(convergence, markov, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    write_csv(destination/'convergence.csv', convergence['rows'])
    batch_rows = []
    for row, values in zip(convergence['rows'], convergence['batches']):
        for i, value in enumerate(values, 1):
            batch_rows.append({'photons_per_batch': row['photons_per_batch'], 'replicate': i,
                               'deposited_mev_per_primary': value[0], 'escaped_mev_per_primary': value[1]})
    write_csv(destination/'transport_batches.csv', batch_rows)
    metadata = {k:v for k,v in convergence.items() if k not in ('rows','batches')}
    metadata['total_transport_photons'] = sum(row['total_transport_photons'] for row in convergence['rows'])
    metadata['transport_parameters'] = {'source_energy_mev': 1.0, 'box_length_cm': 10.0,
                                        'cutoff_mev': 0.05, 'max_interactions': 200}
    metadata['environment'] = {'python': platform.python_version(),
                               **{name:version(name) for name in ('numpy','scipy','matplotlib')}}
    (destination/'convergence_summary.json').write_text(json.dumps(metadata, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (destination/'markov_summary.json').write_text(json.dumps(markov['summary'], indent=2, allow_nan=False)+'\n', encoding='utf-8')
    np.savetxt(destination/'transition_matrix.csv', markov['chain']['matrix'], delimiter=',', fmt='%.12g')
    from .study_plots import plot_convergence, plot_markov
    plot_convergence(convergence, destination/'convergence.png')
    plot_markov(markov, destination/'markov.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='Small integration run, not the published experiment')
    parser.add_argument('--replicates', type=int, default=24)
    parser.add_argument('--seed', type=int, default=20261018)
    parser.add_argument('--material', choices=MATERIALS, default='legacy-water')
    parser.add_argument('--output', type=Path, default=Path('output/studies'))
    args = parser.parse_args()
    try:
        counts = (30, 100) if args.quick else (100, 300, 1000, 3000)
        result = convergence_study(counts, 4 if args.quick else args.replicates, args.seed, args.material)
        chain = markov_study(1000 if args.quick else 50000, args.seed+1)
        save_studies(result, chain, args.output)
    except (ValueError, RuntimeError) as error:
        parser.exit(2, f'Error: {error}\n')
    print(f"Saved {'quick checks' if args.quick else 'full studies'} to {args.output}")
    print(f"Transport batch-SD log-log slope: {result['sd_log_log_slope']}")
    print(json.dumps(chain['summary'], indent=2))


if __name__ == '__main__':
    main()
