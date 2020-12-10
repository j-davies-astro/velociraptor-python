"""
Objects for handling and plotting mean and median lines.
"""

from unyt import unyt_quantity, unyt_array
from numpy import logspace, linspace, log10, logical_and
from typing import Dict, Union, Tuple, List
from matplotlib.pyplot import Axes

import velociraptor.tools.lines as lines
from velociraptor.tools.mass_functions import (
    create_mass_function_given_bins,
    create_adaptive_mass_function,
)
from velociraptor.tools.histogram import create_histogram_given_bins
from velociraptor.tools.adaptive import create_adaptive_bins

valid_line_types = [
    "median",
    "mean",
    "mass_function",
    "histogram",
    "cumulative_histogram",
    "adaptive_mass_function",
]


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
    histogram: bool
    cumulative_histogram: bool
    adaptive_mass_function: bool
    # Create bins in logspace?
    log: bool
    # Binning properties
    number_of_bins: int
    start: unyt_quantity
    end: unyt_quantity
    lower: unyt_quantity
    upper: unyt_quantity
    # Use adaptive binning?
    adaptive: bool
    bins: unyt_array = None
    # Scatter can be: "none", "errorbar", or "shaded"
    scatter: str
    # Output: centers, values, scatter, additional_x, additional_y - initialised here
    # to prevent crashes in other code.
    output: Tuple[unyt_array] = (
        unyt_array([]),
        unyt_array([]),
        unyt_array([]),
        unyt_array([]),
        unyt_array([]),
    )

    def __init__(self, line_type: str, line_data: Dict[str, Union[Dict, str]]):
        """
        Initialise a line with data from the yaml file.
        """

        self.line_type = line_type
        self._parse_line_type()

        self.data = line_data
        self._parse_data()

        return

    def _parse_line_type(self):
        """
        Parse the line type to a boolean.
        """

        # TODO: Use centralised metadata for this list.
        for line_type in valid_line_types:
            setattr(self, line_type, self.line_type == line_type)

        return

    def _parse_data(self):
        """
        Parse the line data from the dictionary and set defaults.
        """

        self.plot = bool(self.data.get("plot", True))
        self.log = bool(self.data.get("log", True))
        self.number_of_bins = int(self.data.get("number_of_bins", 25))
        self.scatter = str(self.data.get("scatter", "shaded"))
        self.adaptive = bool(self.data.get("adaptive", False))

        if self.scatter not in ["none", "errorbar", "shaded"]:
            self.scatter = "shaded"

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

        return

    def generate_bins(self, values=None):
        """
        Generates the required bins. If we request adaptive bins, this is a little
        more complicated and requires the values along the horizontal axis.
        """

        if values is not None and self.adaptive:
            self.end.convert_to_units(values.units)
            self.start.convert_to_units(self.end.units)

            bin_centers, bin_edges = create_adaptive_bins(
                values=values,
                lowest_value=self.start,
                highest_value=self.end,
                base_n_bins=self.number_of_bins,
                logarithmic=self.log,
                stretch_final_bin="mass_function" in self.line_type,
            )

            self.bins = bin_edges
        else:
            # Assert these are in the same units just in case
            self.start.convert_to_units(self.end.units)

            if self.log:
                # Need to strip units, unfortunately
                self.bins = unyt_array(
                    logspace(
                        log10(self.start.value),
                        log10(self.end.value),
                        self.number_of_bins,
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
        reverse_cumsum: bool = False,
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

        reverse_cumsum: bool
            A boolean deciding whether to reverse the cumulative sum. If false,
            the sum is computed from low to high values (along the X-axis). Relevant
            only for cumulative histogram lines. Default is false.

        Returns
        -------

        output: Tuple[unyt_array]
            A five-length (mean, median lines) or three-length (mass_function,
            histogram, cumulative_histogram) tuple of unyt arrays that takes the
            following form: (bin centers, vertical values, vertical scatter,
            additional_x [optional], additional_y [optional]).
        """

        if self.bins is None:
            self.generate_bins(values=x)
        else:
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
                x=masked_x, y=masked_y, x_bins=self.bins, return_additional=True
            )
        elif self.mean:
            self.output = lines.binned_mean_line(
                x=masked_x, y=masked_y, x_bins=self.bins, return_additional=True
            )
        elif self.mass_function:
            mass_function_output = create_mass_function_given_bins(
                masked_x, self.bins, box_volume=box_volume
            )
            self.output = (
                *mass_function_output,
                unyt_array([], units=mass_function_output[0].units),
                unyt_array([], units=mass_function_output[1].units),
            )
        elif self.histogram:
            histogram_output = create_histogram_given_bins(
                masked_x, self.bins, box_volume=box_volume
            )
            self.output = (
                *histogram_output,
                unyt_array([], units=histogram_output[0].units),
                unyt_array([], units=histogram_output[1].units),
            )
        elif self.cumulative_histogram:
            histogram_output = create_histogram_given_bins(
                masked_x,
                self.bins,
                box_volume=box_volume,
                cumulative=True,
                reverse=reverse_cumsum,
            )
            self.output = (
                *histogram_output,
                unyt_array([], units=histogram_output[0].units),
                unyt_array([], units=histogram_output[1].units),
            )
        elif self.adaptive_mass_function:
            *mass_function_output, self.bins = create_adaptive_mass_function(
                masked_x,
                lowest_mass=self.start,
                highest_mass=self.end,
                box_volume=box_volume,
                return_bin_edges=True,
            )
            self.output = (
                *mass_function_output,
                unyt_array([], units=mass_function_output[0].units),
                unyt_array([], units=mass_function_output[1].units),
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

        centers, heights, errors, additional_x, additional_y = self.create_line(
            x=x, y=y
        )

        if self.scatter == "none" or errors is None:
            ax.plot(centers, heights, label=label)
        elif self.scatter == "errorbar":
            ax.errorbar(centers, heights, yerr=errors, label=label)
        elif self.scatter == "errorbar_both":
            ax.errorbar(
                centers,
                heights,
                yerr=errors,
                xerr=abs(self.bins - centers),
                label=label,
                fmt=".",  # Do not plot as a line.
            )
        elif self.scatter == "shaded":
            (line,) = ax.plot(centers, heights, label=label)

            # Deal with different + and -ve errors
            if errors.shape[0]:
                if errors.ndim > 1:
                    down, up = errors
                else:
                    up = errors
                    down = errors
            else:
                up = unyt_quantity(0, units=heights.units)
                down = unyt_quantity(0, units=heights.units)

            ax.fill_between(
                centers,
                heights - down,
                heights + up,
                color=line.get_color(),
                alpha=0.3,
                linewidth=0.0,
            )

        return
