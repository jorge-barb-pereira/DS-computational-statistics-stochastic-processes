"""Exact absorbing Markov chain for binned first-interaction slab transport.

Transient state i means alive at the left edge of bin i. Absorbed and
transmitted are terminal states. This is not an energy-only approximation
to the three-dimensional scattering process.
"""
import math
import numpy as np
from .transport import positive_integer


def slab_chain(mu=0.771, length=2.0, step=0.1):
    if any(not math.isfinite(v) or v <= 0 for v in (mu, length, step)):
        raise ValueError('mu, length and step must be positive and finite')
    if math.ceil(length/step) > 500:
        raise ValueError('Dense-chain study is limited to 500 transient states')
    edges = np.unique(np.r_[np.arange(0, length, step), length])
    widths = np.diff(edges)
    count = len(widths)
    survival = np.exp(-mu*widths)
    interaction = -np.expm1(-mu*widths)
    matrix = np.zeros((count+2, count+2))
    for i in range(count):
        matrix[i, count] = interaction[i]
        matrix[i, i+1 if i+1 < count else count+1] = survival[i]
    matrix[count, count] = matrix[count+1, count+1] = 1
    q = matrix[:count, :count]
    fundamental = np.linalg.solve(np.eye(count)-q, np.eye(count))
    absorption = fundamental @ matrix[:count, count:]
    expected_steps = fundamental @ np.ones(count)
    first_interaction = np.exp(-mu*edges[:-1])*interaction
    return {'matrix': matrix, 'edges_cm': edges, 'fundamental': fundamental,
            'absorption_probabilities': absorption, 'expected_steps': expected_steps,
            'first_interaction_probabilities': first_interaction,
            'mu': mu, 'length_cm': length, 'step_cm': step}


def sample_slab_chain(chain, photons=50000, seed=20261018):
    """Simulate independent paths; each path ends after at most n_bins steps."""
    positive_integer(photons, 'photons')
    matrix = chain['matrix']
    count = len(chain['edges_cm'])-1
    rng = np.random.default_rng(seed)
    alive = np.ones(photons, dtype=bool)
    steps = np.zeros(photons, dtype=int)
    interactions = np.zeros(count, dtype=int)
    survivors = [photons]
    for i in range(count):
        indices = np.flatnonzero(alive)
        steps[indices] += 1
        absorbed = indices[rng.random(len(indices)) < matrix[i, count]]
        alive[absorbed] = False
        interactions[i] = len(absorbed)
        survivors.append(int(alive.sum()))
    return {'photons': photons, 'absorbed': int((~alive).sum()), 'transmitted': int(alive.sum()),
            'interaction_counts': interactions, 'survivor_counts': np.array(survivors),
            'steps_per_path': steps}
