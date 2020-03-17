"""
Tools to generate various lines from datasets.
"""

import unyt
import numpy as np

from typing import List


def binned_mean_line(
    x: unyt.unyt_array,
    y: unyt.unyt_array,
    x_bins: unyt.unyt_array,
    minimum_in_bin: int = 3,
):
    """
    Gets a mean (y) line, binned in the x direction.

    Parameters
    ----------

    x: unyt.unyt_array
        Horizontal values, to be binned.

    y: unyt.unyt_array
        Vertical values, to have the mean calculated in the x-bins

    x_bins: unyt.unyt_array
        Horizontal bin edges. Must have the same units as x.

    minimum_in_bin: int, optional
        Minimum number of items in a bin to return that bin. If a bin has
        fewer values than this, it is excluded from the return values.
        Default: 3.


    Returns
    -------

    bin_centers: unyt.unyt_array
        The centers of the bins (taken to be the linear mean of the bin edges).

    means: unyt.unyt_array
        Vertical mean values within the bins.

    standard_deviation: unyt.unyt_array
        Standard deviation within the bins, to be shown as scatter.


    Notes
    -----

    The return types are such that you can pass this directly to `plt.errorbar`,
    as follows:

    .. code-block:: python

        plt.errorbar(
            *binned_mean_line(x, y, x_bins, 10)
        )

    """

    assert (
        x.units == x_bins.units
    ), "Please ensure that the x values and bins have the same units."

    hist = np.digitize(x, x_bins)

    means = []
    standard_deviations = []
    centers = []

    for bin in range(1, len(x_bins)):
        indicies_in_this_bin = hist == bin

        if indicies_in_this_bin.sum() >= minimum_in_bin:
            y_values_in_this_bin = y[indicies_in_this_bin].value

            means.append(np.mean(y_values_in_this_bin))
            standard_deviations.append(np.std(y_values_in_this_bin))

            centers.append(0.5 * (x_bins[bin - 1].value + x_bins[bin].value))

    means *= y.units
    standard_deviations *= y.units
    centers *= x.units

    return centers, means, standard_deviations


def binned_median_line(
    x: unyt.unyt_array,
    y: unyt.unyt_array,
    x_bins: unyt.unyt_array,
    percentiles: List[int] = [16, 84],
    minimum_in_bin: int = 3,
):
    """
    Gets a median (y) line, binned in the x direction.

    Parameters
    ----------

    x: unyt.unyt_array
        Horizontal values, to be binned.

    y: unyt.unyt_array
        Vertical values, to have the median calculated in the x-bins

    x_bins: unyt.unyt_array
        Horizontal bin edges. Must have the same units as x.

    percentiles: List[int], optional
        Percentiles to return as the positive and negative errors. By
        default these are 16 and 84th percentiles.

    minimum_in_bin: int, optional
        Minimum number of items in a bin to return that bin. If a bin has
        fewer values than this, it is excluded from the return values.
        Default: 3.


    Returns
    -------

    bin_centers: unyt.unyt_array
        The centers of the bins (taken to be the linear mean of the bin edges).

    medians: unyt.unyt_array
        Vertical median values within the bins.

    deviations: unyt.unyt_array
        Deviation from median vertically using the ``percentiles`` defined above.
        This has shape 2xN.


    Notes
    -----

    The return types are such that you can pass this directly to `plt.errorbar`,
    as follows:

    .. code-block:: python

        plt.errorbar(
            *binned_median_line(x, y, x_bins, 10)
        )

    """

    assert (
        x.units == x_bins.units
    ), "Please ensure that the x values and bins have the same units."

    hist = np.digitize(x, x_bins)

    medians = []
    deviations = []
    centers = []

    for bin in range(1, len(x_bins)):
        indicies_in_this_bin = hist == bin

        if indicies_in_this_bin.sum() >= minimum_in_bin:
            y_values_in_this_bin = y[indicies_in_this_bin].value

            medians.append(np.median(y_values_in_this_bin))
            deviations.append(np.percentile(y_values_in_this_bin, percentiles))

            centers.append(0.5 * (x_bins[bin - 1].value + x_bins[bin].value))

    medians *= y.units
    deviations *= y.units
    # Percentiles actually gives us the values - we want to be able to use
    # matplotlib's errorbar function
    deviations = abs(deviations.T - medians)
    centers *= x.units

    return centers, medians, deviations

