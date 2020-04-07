"""
Objects for handling and plotting mean and median lines.
"""

from unyt import unyt_quantity, unyt_array
from numpy import logspace, linspace, log10, logical_and
from typing import Dict, Union, Tuple, List
from matplotlib.pyplot import Axes

import velociraptor.tools.lines as lines
from velociraptor.tools.mass_functions import create_mass_function_given_bins


class VelociraptorLine(object):
    """
    A median or mean line and all the information that is
    required for this (e.g. bins, log space, etc.)
    """

    # Forward declarations
    # Actually plot this line?
    plot: bool
    # Is a median, mass function, or a mean line?
    median: bool
    mean: bool
    mass_function: bool
    # Create bins in logspace?
    log: bool
    # Binning properties
    number_of_bins: int
    start: unyt_quantity
    end: unyt_quantity
    lower: unyt_quantity
    upper: unyt_quantity
    bins: unyt_array
    # Scatter can be: "none", "errorbar", or "shaded"
    scatter: str
    # Output: centers, values, scatter - initialised here to prevent crashes
    # in other code.
    output: Tuple[unyt_array] = (unyt_array([]), unyt_array([]), unyt_array([]))

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

        # TODO: Use centralised metadata for this list.
        for line_type in ["median", "mean", "mass_function"]:
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

        try:
            self.lower = unyt_quantity(
                float(self.data["lower"]["value"]), units=self.data["lower"]["units"]
            )
        except KeyError:
            self.lower = None

        try:
            self.upper = unyt_quantity(
                float(self.data["upper"]["value"]), units=self.data["upper"]["units"]
            )
        except KeyError:
            self.upper = None

        try:
            self.scatter = str(self.data["scatter"])
        except KeyError:
            self.scatter = "shaded"

        if self.scatter not in ["none", "errorbar", "shaded"]:
            self.scatter = "shaded"

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

    def create_line(
        self,
        x: unyt_array,
        y: unyt_array,
        box_volume: Union[None, unyt_quantity] = None,
    ):
        """
        Creates the line!

        Parameters
        ----------

        x: unyt_array
            Horizontal axis data
        
        y: unyt_array
            Vertical axis data

        box_volume: Union[None, unyt_quantity]
            Box volume for the simulation, required for mass functions. Should
            have associated volume units. Generally this is given as a comoving
            quantity.

        Returns
        -------

        output: Tuple[unyt_array]
            A three-length tuple of unyt arrays that takes the following form:
            (bin centers, vertical values, vertical scatter).

        """

        self.bins.convert_to_units(x.units)
        self.output = None

        masked_x = x
        masked_y = y

        if self.lower is not None:
            self.lower.convert_to_units(y.units)
            mask = masked_y > self.lower
            masked_x = masked_x[mask]
            masked_y = masked_y[mask]

        if self.upper is not None:
            self.upper.convert_to_units(y.units)
            mask = masked_y < self.upper
            masked_x = masked_x[mask]
            masked_y = masked_y[mask]

        if self.median:
            self.output = lines.binned_median_line(
                x=masked_x, y=masked_y, x_bins=self.bins
            )
        elif self.mean:
            self.output = lines.binned_mean_line(
                x=masked_x, y=masked_y, x_bins=self.bins
            )
        elif self.mass_function:
            self.output = create_mass_function_given_bins(
                masked_x, self.bins, box_volume=box_volume
            )
        else:
            self.output = None

        return self.output

    def plot_line(
        self, ax: Axes, x: unyt_array, y: unyt_array, label: Union[str, None] = None
    ):
        """
        Plot a line using these parameters on some axes, x against y.

        Parameters
        ----------

        ax: Axes
            Matplotlib axes to plot on.

        x: unyt_array
            Horizontal axis data
        
        y: unyt_array
            Vertical axis data

        label: str
            Label associated with this data that will be included in the
            legend.

        Notes
        -----

        If self.scatter is set to "none", this is plotted assuming the scatter
        is zero.
        """

        if not self.plot:
            return

        centers, heights, errors = self.create_line(x=x, y=y)

        if self.scatter == "none":
            ax.plot(centers, heights, label=label)
        elif self.scatter == "errorbar":
            ax.errorbar(centers, heights, yerr=errors, label=label)
        elif self.scatter == "shaded":
            line, = ax.plot(centers, heights, label=label)

            # Deal with different + and -ve errors
            if errors.shape[0]:
                if errors.ndim > 1:
                    down, up = errors
                else:
                    up = errors
                    down = errors
            else:
                up = 0
                down = 0

            ax.fill_between(
                centers,
                heights - down,
                heights + up,
                color=line.get_color(),
                alpha=0.3,
                linewidth=0.0,
            )

        return
