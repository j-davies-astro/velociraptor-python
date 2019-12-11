"""
Objects for handling and plotting mean and median lines.
"""

from unyt import unyt_quantity, unyt_array
from numpy import logspace, linspace, log10
from typing import Dict, Union, Tuple, List
from matplotlib.pyplot import Axes

import velociraptor.tools.lines as lines


class VelociraptorLine(object):
    """
    A median or mean line and all the information that is
    required for this (e.g. bins, log space, etc.)
    """

    # Forward declarations
    # Actually plot this line?
    plot: bool
    # Is a median or a mean line?
    median: bool
    mean: bool
    # Create bins in logspace?
    log: bool
    # Binning properties
    number_of_bins: int
    start: unyt_quantity
    end: unyt_quantity
    bins: unyt_array

    def __init__(self, line_type: str, line_data: Dict[str, Union[Dict, str]]):
        """
        Initialise a line with data from the yaml file.
        """

        self.line_type = line_type
        self._parse_line_type()

        self.data = line_data
        self._parse_data()

        self.generate_bins()

        return

    def _parse_line_type(self):
        """
        Parse the line type to a boolean.
        """

        for line_type in ["median", "mean"]:
            setattr(self, line_type, self.line_type == line_type)

        return

    def _parse_data(self):
        """
        Parse the line data from the dictionary and set defaults.
        """

        try:
            self.plot = bool(self.data["plot"])
        except KeyError:
            self.plot = True  # Otherwise why would they include this section?

        if not self.plot:
            # Why bother parsing if we are not going to use this line?
            return

        try:
            self.log = bool(self.data["log"])
        except KeyError:
            self.log = True

        try:
            self.number_of_bins = int(self.data["number_of_bins"])
        except KeyError:
            self.number_of_bins = 25

        try:
            self.start = unyt_quantity(
                float(self.data["start"]["value"]), units=self.data["start"]["units"]
            )
        except KeyError:
            self.start = unyt_quantity(0.0)

        try:
            self.end = unyt_quantity(
                float(self.data["end"]["value"]), units=self.data["end"]["units"]
            )
        except KeyError:
            self.end = unyt_quantity(0.0)

        return

    def generate_bins(self):
        """
        Generates the required bins.
        """

        # Assert these are in the same units just in case
        self.start.convert_to_units(self.end.units)

        if self.log:
            # Need to strip units, unfortunately
            self.bins = unyt_array(
                logspace(
                    log10(self.start.value), log10(self.end.value), self.number_of_bins
                ),
                units=self.start.units,
            )
        else:
            # Can get away with this one without stripping
            self.bins = linspace(self.start, self.end, self.number_of_bins)

        return

    def create_line(self, x: unyt_array, y: unyt_array):
        """
        Creates the line!
        """

        self.bins.convert_to_units(x.units)

        if self.median:
            return lines.binned_median_line(x=x, y=y, x_bins=self.bins)
        elif self.mean:
            return lines.binned_mean_line(x=x, y=y, x_bins=self.bins)
        else:
            return None

    def plot_line(
        self, ax: Axes, x: unyt_array, y: unyt_array, label: Union[str, None] = None
    ):
        """
        Plot a line using these parameters on some axes, x against y.
        """

        if not self.plot:
            return

        centers, heights, errors = self.create_line(x=x, y=y)

        ax.errorbar(centers, heights, yerr=errors, label=label)

        return
