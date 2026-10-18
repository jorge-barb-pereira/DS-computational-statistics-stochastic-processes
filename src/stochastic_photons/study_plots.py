"""Figures for explicitly scoped convergence and absorbing-chain studies."""
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t


def plot_convergence(study, destination):
    rows = study['rows']
    n = np.array([r['photons_per_batch'] for r in rows])
    sd = np.array([r['sd_deposited_mev_per_primary'] for r in rows])
    mean = np.array([r['mean_deposited_mev_per_primary'] for r in rows])
    half = np.array([r['ci95_deposited_upper']-r['mean_deposited_mev_per_primary'] for r in rows])
    fig, axes = plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    fig.suptitle(f"Monte Carlo sampling convergence: {study['replicates']} independent batches per N\n"
                 f"3D transport: {study['material']}; separate analytic slab benchmark")
    ax = axes[0,0]
    ax.loglog(n, [r['transmission_rmse'] for r in rows], 'o-', label='Empirical RMSE')
    ax.loglog(n, [r['theoretical_transmission_rmse'] for r in rows], '--', label='Exact binomial RMSE')
    ax.set(title='Analytic first-interaction slab benchmark', xlabel='Photons per independent batch', ylabel='Transmission probability RMSE')
    ax.legend()
    ax = axes[0,1]
    ax.loglog(n, sd, 'o-', label='3D deposition: batch SD')
    ax.loglog(n, sd[0]*np.sqrt(n[0]/n), '--', label='N^(-1/2), anchored at first point')
    slope = study['sd_log_log_slope']
    ax.set(title=f"Transport estimator dispersion (slope {slope:.3f})" if slope is not None else 'Transport estimator dispersion',
           xlabel='Photons per independent batch', ylabel='SD of deposited MeV / primary')
    ax.legend()
    ax = axes[1,0]
    ax.errorbar(n, mean, yerr=half, fmt='o-', capsize=4)
    ax.set_xscale('log')
    ax.set(title='Transport grand means: approximate 95% t intervals', xlabel='Photons per independent batch', ylabel='Mean deposited MeV / primary')
    ax = axes[1,1]
    values = study['batches'][-1][:,0]
    k = np.arange(2, len(values)+1)
    averages = np.array([values[:j].mean() for j in k])
    half = np.array([t.ppf(0.975,j-1)*values[:j].std(ddof=1)/np.sqrt(j) for j in k])
    ax.plot(k, averages)
    ax.fill_between(k, averages-half, averages+half, alpha=0.2)
    ax.set(title=f'Running mean at N = {n[-1]:,} (descriptive intervals)', xlabel='Independent batches accumulated', ylabel='Mean deposited MeV / primary')
    fig.savefig(destination, dpi=140)
    plt.close(fig)


def plot_markov(study, destination):
    chain, sample, summary = study['chain'], study['sample'], study['summary']
    n = summary['transient_states']
    edges = chain['edges_cm']
    fig, axes = plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    fig.suptitle(f"Absorbing Markov chain: first interaction in a {chain['length_cm']:g} cm slab\n"
                 f"{sample['photons']:,} independent paths; illustrative mu = {chain['mu']:g} cm^-1")
    ax = axes[0,0]
    im = ax.imshow(chain['matrix'], vmin=0, vmax=1, cmap='viridis')
    ticks = [0, n//2, n-1, n, n+1]
    labels = ['S0', f'S{n//2}', f'S{n-1}', 'A', 'T']
    ax.set(xticks=ticks, xticklabels=labels, yticks=ticks, yticklabels=labels,
           title='Transition matrix P: A and T are absorbing', xlabel='Next state', ylabel='Current state')
    ax.tick_params(axis='x', labelrotation=45, labelsize=8)
    fig.colorbar(im, ax=ax, label='Transition probability')
    ax = axes[0,1]
    ax.plot(edges, np.exp(-chain['mu']*edges), label='Exact exponential survival')
    ax.step(edges, sample['survivor_counts']/sample['photons'], where='post', label='Simulated survival', alpha=0.8)
    ax.set(title='Alive probability at bin boundaries', xlabel='Depth (cm)', ylabel='Survival probability')
    ax.legend()
    ax = axes[1,0]
    ax.plot(edges[1:], chain['first_interaction_probabilities'], label='Exact first-interaction probability')
    ax.plot(edges[1:], sample['interaction_counts']/sample['photons'], 'o', ms=3, label='Simulated bin frequencies')
    ax.set(title='Absorption location (unconditional)', xlabel='Right endpoint of bin (cm)', ylabel='Probability per incident photon')
    ax.legend()
    ax = axes[1,1]
    exact = chain['absorption_probabilities'][0]
    empirical = np.array([sample['absorbed'],sample['transmitted']])/sample['photons']
    x = np.arange(2)
    ax.bar(x-0.18, exact, width=0.36, label='Matrix solution')
    ax.bar(x+0.18, empirical, width=0.36, label='Simulated paths')
    ax.set(xticks=x, xticklabels=['Absorbed', 'Transmitted'], ylim=(0,1), ylabel='Terminal probability',
           title=f"Mean steps: exact {summary['exact_expected_steps']:.3f}, simulated {summary['empirical_expected_steps']:.3f}")
    ax.legend()
    fig.savefig(destination, dpi=140)
    plt.close(fig)
