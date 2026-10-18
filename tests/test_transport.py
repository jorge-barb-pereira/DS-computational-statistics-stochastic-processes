import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from stochastic_photons.transport import (
    MATERIALS, compton_event, scatter_direction, simulate_batch, simulate_ensemble, voxel_index,
)


class TransportTests(unittest.TestCase):
    def test_energy_conservation_for_both_materials(self):
        for material in MATERIALS:
            for limit in (1, 200):
                batch = simulate_batch(photons=150, material=material, grid_size=8, max_interactions=limit)
                total = sum(batch[k] for k in ('deposited_mev', 'escaped_mev', 'unresolved_mev'))
                self.assertAlmostEqual(total, batch['source_mev'], places=10)
                self.assertGreaterEqual(batch['cutoff_deposited_mev'], 0)
                self.assertLessEqual(batch['cutoff_deposited_mev'], batch['deposited_mev'] + 1e-12)
                self.assertTrue(np.all(batch['grid'] >= 0))

    def test_cutoff_ledger_is_subset_of_deposition(self):
        b = simulate_batch(photons=10, energy=0.05, cutoff=0.05, grid_size=4)
        self.assertAlmostEqual(b['deposited_mev'], 0.5)
        self.assertAlmostEqual(b['cutoff_deposited_mev'], 0.5)
        self.assertEqual(b['escaped_mev'], 0)

    def test_reproducibility(self):
        a = simulate_batch(photons=50, grid_size=6, seed=7)
        b = simulate_batch(photons=50, grid_size=6, seed=7)
        np.testing.assert_array_equal(a.pop('grid'), b.pop('grid'))
        self.assertEqual(a, b)

    def test_rotations_at_poles_and_diagonal(self):
        for u in ([0,0,1], [0,0,-1], [1,1,1]):
            for cosine in (-1, -0.3, 0, 1):
                direction = scatter_direction(u, cosine, 1.7)
                self.assertAlmostEqual(np.linalg.norm(direction), 1)
                self.assertAlmostEqual(np.dot(direction, np.array(u)/np.linalg.norm(u)), cosine)

    def test_compton_kinematics(self):
        rng = np.random.default_rng(4)
        for energy in (0.05, 0.5, 1):
            for _ in range(100):
                cosine, outgoing = compton_event(energy, rng)
                self.assertTrue(-1 <= cosine <= 1)
                self.assertTrue(0 < outgoing <= energy)
                self.assertAlmostEqual(1/outgoing - 1/energy, (1-cosine)/0.511)

    def test_voxel_boundary_convention(self):
        self.assertEqual(voxel_index([0, 0, 0], 10, (10,10,10)), (0,0,0))
        self.assertEqual(voxel_index([9.999]*3, 10, (10,10,10)), (9,9,9))
        self.assertIsNone(voxel_index([10, 0, 0], 10, (10,10,10)))
        self.assertIsNone(voxel_index([-0.001, 0, 0], 10, (10,10,10)))

    def test_streaming_mean_and_sem_match_batch_statistics(self):
        grids = [simulate_batch(photons=30, grid_size=6, seed=s)['grid']/30
                 for s in np.random.SeedSequence(17).spawn(4)]
        ensemble = simulate_ensemble(histories=4, photons=30, grid_size=6, seed=17)
        np.testing.assert_allclose(ensemble['mean_mev_per_primary'], np.mean(grids, axis=0), atol=1e-16)
        np.testing.assert_allclose(ensemble['sem_mev_per_primary'], np.std(grids, axis=0, ddof=1)/2, atol=1e-16)

    def test_invalid_inputs_and_table_bounds(self):
        for kw in ({'photons':0}, {'photons':True}, {'grid_size':129}, {'energy':0.01},
                   {'energy':2}, {'length':float('nan')}, {'material':'unknown'}, {'cutoff':0.01}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                simulate_batch(**kw)
        with self.assertRaises(ValueError):
            simulate_ensemble(histories=1)
        with self.assertRaises(ValueError):
            scatter_direction([0,0,0], 0, 0)

    def test_cli_produces_readable_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-m', 'stochastic_photons', '--histories', '2',
                                     '--photons', '10', '--grid-size', '6', '--output', directory],
                                    check=True, capture_output=True, text=True, env=dict(os.environ, MPLBACKEND='Agg'))
            self.assertTrue(result.stdout)
            files = list(Path(directory).iterdir())
            self.assertTrue(any(p.suffix == '.png' for p in files))
            summary = json.loads((Path(directory)/'summary.json').read_text())
            self.assertEqual(summary['histories'], 2)
            with np.load(Path(directory)/'transport.npz') as data:
                self.assertTrue(data.files)


if __name__ == '__main__':
    unittest.main()
