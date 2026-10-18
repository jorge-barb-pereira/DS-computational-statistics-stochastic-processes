import unittest
import numpy as np

from stochastic_photons.markov import slab_chain, sample_slab_chain
from stochastic_photons.studies import convergence_study, wilson_interval


class MarkovTests(unittest.TestCase):
    def test_stochastic_matrix_and_absorbing_states(self):
        chain = slab_chain(length=2.05)
        p = chain['matrix']
        self.assertTrue(np.all((p >= 0) & (p <= 1)))
        np.testing.assert_allclose(p.sum(axis=1), 1, atol=1e-15)
        np.testing.assert_array_equal(p[-2:,-2:], np.eye(2))
        self.assertEqual(chain['edges_cm'][-1], 2.05)

    def test_matrix_solution_matches_independent_closed_form(self):
        for mu, length, step in ((0.771,2,0.1),(0.2,1.05,0.2),(1000,1,0.2)):
            chain = slab_chain(mu, length, step)
            edges = chain['edges_cm']
            transmission = np.exp(-mu*(length-edges[:-1]))
            np.testing.assert_allclose(chain['absorption_probabilities'][:,1], transmission, atol=1e-14)
            np.testing.assert_allclose(chain['absorption_probabilities'].sum(axis=1), 1, atol=1e-14)
            self.assertAlmostEqual(chain['expected_steps'][0], np.exp(-mu*edges[:-1]).sum(), places=12)
            self.assertAlmostEqual(chain['first_interaction_probabilities'].sum()+np.exp(-mu*length), 1)

    def test_path_simulation_agrees_with_analytic_distribution(self):
        chain = slab_chain()
        n = 50000
        sample = sample_slab_chain(chain, n, seed=9)
        p = np.exp(-chain['mu']*chain['length_cm'])
        self.assertEqual(sample['absorbed']+sample['transmitted'], n)
        self.assertEqual(sample['interaction_counts'].sum(), sample['absorbed'])
        self.assertLess(abs(sample['transmitted']-n*p), 6*np.sqrt(n*p*(1-p)))
        # First-passage duration has an exactly computable finite distribution.
        masses = chain['first_interaction_probabilities'].copy()
        masses[-1] += p
        durations = np.arange(1,len(masses)+1)
        mean = np.dot(durations,masses)
        variance = np.dot((durations-mean)**2,masses)
        self.assertLess(abs(sample['steps_per_path'].mean()-mean),6*np.sqrt(variance/n))
        repeated = sample_slab_chain(chain,n,seed=9)
        np.testing.assert_array_equal(sample['steps_per_path'],repeated['steps_per_path'])

    def test_invalid_chain_parameters(self):
        for kwargs in ({'mu':0},{'step':-1},{'length':float('nan')},{'step':0.00001}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                slab_chain(**kwargs)


class ConvergenceTests(unittest.TestCase):
    def test_wilson_reference_and_boundary_counts(self):
        lower,upper = wilson_interval(50,100)
        self.assertAlmostEqual(lower,0.4038315304,places=9)
        self.assertAlmostEqual(upper,0.5961684696,places=9)
        self.assertEqual(wilson_interval(0,10)[0],0)
        self.assertAlmostEqual(wilson_interval(10,10)[1],1)

    def test_small_study_outputs_and_analytic_scaling(self):
        study = convergence_study((20,80),replicates=4,seed=16,grid_size=4)
        low,high = study['rows']
        self.assertAlmostEqual(low['theoretical_transmission_rmse']/high['theoretical_transmission_rmse'],2)
        self.assertEqual(high['total_transport_photons'],320)
        for row in study['rows']:
            self.assertLessEqual(row['ci95_deposited_lower'],row['mean_deposited_mev_per_primary'])
            self.assertGreaterEqual(row['ci95_deposited_upper'],row['mean_deposited_mev_per_primary'])
            self.assertTrue(0 <= row['wilson_coverage_fraction'] <= 1)
            self.assertAlmostEqual(row['mean_deposited_mev_per_primary']+row['mean_escaped_mev_per_primary'],1)
        repeated = convergence_study((20,80),replicates=4,seed=16,grid_size=4)
        self.assertEqual(study['rows'],repeated['rows'])

    def test_invalid_design(self):
        for kwargs in ({'photon_counts':(10,)},{'photon_counts':(10,5)},
                       {'photon_counts':(10,True)},{'replicates':2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                convergence_study(**kwargs)


if __name__ == '__main__':
    unittest.main()
