"""Small educational photon-transport model with explicit energy accounting.

The coefficient arrays come from the supplied notebook and are not validated
material data. Only photoelectric absorption and free-electron Compton scattering
are represented. Deposited energy is not absorbed dose.
"""
from dataclasses import dataclass
import math
import numpy as np


def positive_integer(value, name, minimum=1):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')


@dataclass(frozen=True)
class Material:
    name: str
    density: float
    energies: tuple
    photo: tuple
    compton: tuple

    def __post_init__(self):
        if not math.isfinite(self.density) or self.density <= 0:
            raise ValueError('Material density must be finite and positive')
        e, p, c = [np.asarray(x, dtype=float) for x in (self.energies, self.photo, self.compton)]
        if e.ndim != 1 or len(e) < 2 or e.shape != p.shape or e.shape != c.shape:
            raise ValueError('Coefficient tables must have matching one-dimensional shapes')
        if not all(np.isfinite(x).all() for x in (e, p, c)) or (e <= 0).any() or (np.diff(e) <= 0).any():
            raise ValueError('Energy grid must be finite, positive and strictly increasing')
        if (p < 0).any() or (c < 0).any() or ((p+c) <= 0).any():
            raise ValueError('Partial coefficients must be nonnegative with positive totals')

    def coefficients(self, energy):
        if not math.isfinite(energy) or not self.energies[0] <= energy <= self.energies[-1]:
            raise ValueError('Energy is outside the supplied coefficient table; extrapolation is disabled')
        photo = float(np.interp(energy, self.energies, self.photo))
        compton = float(np.interp(energy, self.energies, self.compton))
        # Use the sum of modeled partial coefficients consistently, not a total
        # containing omitted interactions such as coherent scattering.
        return self.density * (photo+compton), photo/(photo+compton)


ENERGIES = (0.05, 0.1, 0.5, 1.0)
MATERIALS = {
    'legacy-lead': Material('Legacy-inspired lead table', 11.34, ENERGIES,
                           (7.292, 5.237, 0.08257, 0.01810),
                           (0.09478, 0.09894, 0.06734, 0.04993)),
    'legacy-water': Material('Legacy-inspired water table', 1.0, ENERGIES,
                            (0.02725, 0.002763, 0.00001883, 0.000003681),
                            (0.1803, 0.1626, 0.09663, 0.07066)),
}


def normalized(direction):
    direction = np.asarray(direction, dtype=float)
    if direction.shape != (3,) or not np.isfinite(direction).all() or np.linalg.norm(direction) == 0:
        raise ValueError('Direction must be a finite nonzero 3-vector')
    return direction / np.linalg.norm(direction)


def scatter_direction(direction, cosine, azimuth):
    """Rotate about any unit direction, including both axial poles."""
    if not math.isfinite(cosine) or not -1 <= cosine <= 1 or not math.isfinite(azimuth):
        raise ValueError('Scattering angles must be finite with cosine in [-1,1]')
    u = normalized(direction)
    axis = np.eye(3)[np.argmin(np.abs(u))]
    v = normalized(np.cross(u, axis))
    w = np.cross(u, v)
    sine = math.sqrt(max(0, 1-cosine*cosine))
    return normalized(cosine*u + sine*(math.cos(azimuth)*v + math.sin(azimuth)*w))


def compton_event(energy, rng):
    """Sample a free-electron Klein–Nishina angle using a bounded rejection loop."""
    if not math.isfinite(energy) or energy <= 0:
        raise ValueError('Energy must be finite and positive')
    for _ in range(100000):
        cosine = float(rng.uniform(-1, 1))
        ratio = 1/(1+(energy/0.511)*(1-cosine))
        weight = ratio*ratio*(ratio+1/ratio-(1-cosine*cosine))
        if rng.uniform(0, 2) < weight:
            return cosine, energy*ratio
    raise RuntimeError('Compton rejection sampler failed to converge')


def voxel_index(position, length, shape):
    position = np.asarray(position, dtype=float)
    if position.shape != (3,) or not np.isfinite(position).all():
        raise ValueError('Position must be a finite 3-vector')
    if (position < 0).any() or (position >= length).any():
        return None
    return tuple(np.floor(position/length*np.asarray(shape)).astype(int))


def simulate_batch(photons=1000, grid_size=24, length=10.0, material='legacy-lead',
                   energy=1.0, cutoff=0.05, seed=42, max_interactions=200):
    positive_integer(photons, 'photons')
    positive_integer(grid_size, 'grid_size', 2)
    positive_integer(max_interactions, 'max_interactions')
    if grid_size > 128:
        raise ValueError('Grid size exceeds the bounded demo limit of 128 voxels per axis')
    if not math.isfinite(length) or length <= 0:
        raise ValueError('Box length must be finite and positive')
    if material not in MATERIALS:
        raise ValueError('Unknown material table')
    table = MATERIALS[material]
    table.coefficients(energy)
    if not math.isfinite(cutoff) or not table.energies[0] <= cutoff <= energy:
        raise ValueError('Cutoff must lie within the table range and not exceed source energy')
    rng = np.random.default_rng(seed)
    grid = np.zeros((grid_size,)*3)
    escaped = unresolved = cutoff_deposited = 0.0
    for _ in range(photons):
        position = np.array([length/2, length/2, 0.0])
        direction = np.array([0.0, 0.0, 1.0])
        remaining = energy
        for _ in range(max_interactions):
            if remaining <= cutoff:
                index = voxel_index(position, length, grid.shape)
                grid[index] += remaining
                cutoff_deposited += remaining
                break
            attenuation, photo_probability = table.coefficients(remaining)
            distance = float(rng.exponential(1/attenuation))
            position = position + normalized(direction)*distance
            index = voxel_index(position, length, grid.shape)
            if index is None:
                escaped += remaining
                break
            if rng.random() < photo_probability:
                grid[index] += remaining
                break
            cosine, outgoing = compton_event(remaining, rng)
            grid[index] += remaining-outgoing
            remaining = outgoing
            direction = scatter_direction(direction, cosine, float(rng.uniform(0, 2*math.pi)))
        else:
            unresolved += remaining
    return {'grid': grid, 'source_mev': photons*energy, 'deposited_mev': float(grid.sum()),
            'escaped_mev': escaped, 'unresolved_mev': unresolved,
            'cutoff_deposited_mev': cutoff_deposited}


def simulate_ensemble(histories=4, photons=1000, seed=42, **kwargs):
    """Streaming batch means and SEM; memory does not grow with history count."""
    positive_integer(histories, 'histories', 2)
    positive_integer(photons, 'photons')
    children = np.random.SeedSequence(seed).spawn(histories)
    mean = m2 = None
    balances = []
    for count, child in enumerate(children, 1):
        batch = simulate_batch(photons=photons, seed=child, **kwargs)
        grid = batch.pop('grid')/photons
        if mean is None:
            mean = np.zeros_like(grid)
            m2 = np.zeros_like(grid)
        delta = grid-mean
        mean += delta/count
        m2 += delta*(grid-mean)
        balances.append(batch)
    variance = np.maximum(m2/(histories-1), 0)
    return {'mean_mev_per_primary': mean, 'sem_mev_per_primary': np.sqrt(variance/histories),
            'histories': histories, 'photons_per_history': photons, 'energy_balances': balances}
