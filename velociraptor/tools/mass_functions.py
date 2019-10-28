"""
Tools for creating mass functions!
"""

import unyt
import numpy as np


def create_mass_function(
    masses: unyt.unyt_array,
    lowest_mass: unyt.unyt_quantity,
    highest_mass: unyt.unyt_quantity,
    box_volume: unyt.unyt_quantity,
    n_bins: int = 25,
    objects_for_valid_bin: int = 1,
    return_bin_edges: bool = False,
):
    """
    Creates a mass function (with equal width bins in log M) for you to plot.

    Takes:

    + masses, the array that you want to create a mass function of
    + lowest_mass, the lowest mass edge of the bins
    + highest_mass, the highest mass edge of the bins
    + box_volume, the volume of the box such that we can return n / volume
    + n_bins, the number of bins. We will create an array of bins from [lowest_mass, highest_mass]
              inclusive, such that the bins are equally spaced in log(a)
    + objects_for_valid_bin, the number of objects in a bin for it to be classed as
                             valid.
    + return_bin_edges, whether or not to return the bin edges as the fourth return
                        value. Defaults to false, such that you can do:
                        
                           plt.errorbar(*create_mass_function)
                        
                        to get an errorbared plot of the mass function.

    Returns:

    + bin_centers, the centers of the bins that we used
    + mass_function, the value of the mass function at the bin centers
    + error, the satter in the mass function at the bin centers
    + (optional) bin_edges, the edges of the bins used to histogram the data.
    """

    assert (
        masses.units == lowest_mass.units and lowest_mass.units == highest_mass.units,
        "Please ensure that all mass quantities have the same units.",
    )

    bins = (
        np.logspace(np.log10(lowest_mass), np.log10(highest_mass), n_bins + 1)
        * masses.units
    )
    # This is required to ensure that the mass function converges with bin width
    bin_width_in_logspace = np.log10(bins[1]) - np.log10(bins[0])
    normalization_factor = 1.0 / (bin_width_in_logspace * box_volume)

    mass_function, _ = np.histogram(masses, bins)
    valid_bins = mass_function > objects_for_valid_bin

    # Poisson sampling
    error = np.sqrt(mass_function)

    mass_function *= normalization_factor
    error *= normalization_factor

    bin_centers = 0.5 * (bins[1:] + bins[:-1])

    if return_bin_edges:
        return (
            bin_centers[valid_bins],
            mass_function[valid_bins],
            error[valid_bins],
            bins,
        )
    else:
        return bin_centers[valid_bins], mass_function[valid_bins], error[valid_bins]

