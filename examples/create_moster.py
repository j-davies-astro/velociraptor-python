"""
Creates the "moster" plot (stellar mass halo mass relation) and plots on top two of our in-built lines.
"""

import velociraptor as vr
import velociraptor.tools as tools
import velociraptor.fitting_formulae.smhmr as smhmr

import numpy as np
import matplotlib.pyplot as plt
import unyt

import sys

data = vr.load(sys.argv[1])

# Create local pointers to data and convert them to the units we'd like to plot
stellar_masses = data.apertures.mass_star_30_kpc
halo_masses = data.masses.mass_200crit

stellar_masses.convert_to_units(unyt.msun)
halo_masses.convert_to_units(unyt.msun)

stellar_mass_range = [1e6, 1e11] * unyt.msun
halo_mass_range = [1e9, 1e14] * unyt.msun

halo_mass_bins = (
    np.logspace(*np.log10(halo_mass_range.value), 64) * halo_mass_range.units
)

# constrained_layout is similar to tight_layout() but continuous
fig, ax = plt.subplots(constrained_layout=True)
ax.loglog()

# Create background scatter plot of galaxy size data
ax.scatter(
    halo_masses,
    stellar_masses,
    s=1,
    edgecolor="none",
    label="All Galaxies",
    c="grey",
    alpha=0.5,
)

# Only plot median line for values that are reasonable
selection = stellar_masses > stellar_mass_range[0]
ax.errorbar(
    *tools.binned_median_line(
        halo_masses[selection], stellar_masses[selection], halo_mass_bins
    ),
    label="Median",
    marker="o",
    ms=3,
    linestyle="none",
)

# Plot two relations
ax.plot(*smhmr.moster(data), label="Moster+ (2013)")
ax.plot(*smhmr.behroozi(data), label="Behroozi+ (2013)")

# Setting nice limits on the plot...
ax.set_xlim(*halo_mass_range)
ax.set_ylim(*stellar_mass_range)

# Add redshift and scale factor for easy plot identification
ax.text(
    0.05,
    0.95,
    f"$z={data.z:2.3f}$\n$a={data.a:2.3f}$",
    ha="left",
    va="top",
    transform=ax.transAxes,
)

ax.set_xlabel(tools.get_full_label(halo_masses))
ax.set_ylabel(tools.get_full_label(stellar_masses))
ax.legend(loc="lower right", markerfirst=False)

fig.savefig("stellar_mass_halo_mass.pdf")
