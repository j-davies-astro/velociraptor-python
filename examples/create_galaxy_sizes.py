"""
Creates as basic galaxy sizes plot using the velociraptor library.

Please pass the path to the catalogue as your first argument.
"""

import velociraptor as vr
import velociraptor.tools as tools

import numpy as np
import matplotlib.pyplot as plt
import unyt

import sys

data = vr.load(sys.argv[1])

# Create local pointers to data and convert them to the units we'd like to plot
stellar_masses = data.apertures.mass_star_30_kpc
galaxy_sizes = data.apertures.rhalfmass_star_30_kpc

stellar_masses.convert_to_units(unyt.msun)
galaxy_sizes.convert_to_units(unyt.kpc)

stellar_mass_bins = np.logspace(7, 12, 25) * unyt.msun

# constrained_layout is similar to tight_layout() but continuous
fig, ax = plt.subplots(constrained_layout=True)
ax.loglog()

# Create background scatter plot of galaxy size data
ax.scatter(stellar_masses, galaxy_sizes, s=1, edgecolor="none")

# Only plot median line for values that are reasonable
selection = galaxy_sizes > 1e-1 * unyt.kpc
ax.errorbar(
    *tools.binned_median_line(
        stellar_masses[selection], galaxy_sizes[selection], stellar_mass_bins
    )
)

# Setting nice limits on the plot...
ax.set_xlim(stellar_mass_bins[0], stellar_mass_bins[-1])
ax.set_ylim(1e0 * unyt.kpc, 1e1 * unyt.kpc)

# Add redshift and scale factor for easy plot identification
ax.text(
    0.95,
    0.05,
    f"$z={data.z:2.3f}$\n$a={data.a:2.3f}$",
    ha="right",
    va="bottom",
    transform=ax.transAxes,
)

ax.set_xlabel(tools.get_full_label(stellar_masses))
ax.set_ylabel(tools.get_full_label(galaxy_sizes))

fig.savefig("galaxy_sizes.pdf")
