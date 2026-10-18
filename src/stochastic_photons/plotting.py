"""Plot energy tallies without claiming absorbed-dose calibration."""
import matplotlib.pyplot as plt
import numpy as np


def plot_transport(result,length,destination):
    mean = result['mean_mev_per_primary']
    sem = result['sem_mev_per_primary']
    middle = mean.shape[0]//2
    fig, axes = plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    fig.suptitle('Educational Monte Carlo photon transport\nLegacy-inspired coefficient table; energy, not absorbed dose')
    extent=[0,length,0,length]
    maximum=max(float(mean.max()),1e-15)
    for ax,plane,title in [(axes[0,0],mean[:,middle,:].T,'Central XZ energy tally'),
                            (axes[0,1],mean[middle,:,:].T,'Central YZ energy tally')]:
        im=ax.imshow(plane,origin='lower',extent=extent,aspect='equal',cmap='magma',vmin=0,vmax=maximum)
        ax.set(title=title,xlabel='Transverse distance (cm)',ylabel='Depth (cm)')
        fig.colorbar(im,ax=ax,label='MeV / primary / voxel')
    depth=(np.arange(mean.shape[2])+0.5)*length/mean.shape[2]
    axes[1,0].plot(depth,mean.sum(axis=(0,1)),color='#2563eb')
    axes[1,0].set(title='Depth profile (sum over transverse voxels)',xlabel='Depth (cm)',ylabel='MeV / primary / depth bin')
    im=axes[1,1].imshow(sem[:,middle,:].T,origin='lower',extent=extent,aspect='equal',cmap='viridis')
    axes[1,1].set(title=f"Batch SEM ({result['histories']} independent batches)",xlabel='Transverse distance (cm)',ylabel='Depth (cm)')
    fig.colorbar(im,ax=axes[1,1],label='MeV / primary / voxel')
    fig.savefig(destination,dpi=130)
    plt.close(fig)
