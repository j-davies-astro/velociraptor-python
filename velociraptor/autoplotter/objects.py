"""
Main objects for holding information relating to the autoplotter.
"""

from velociraptor import VelociraptorCatalogue
from velociraptor.autoplotter.lines import VelociraptorLine
from velociraptor.exceptions import AutoPlotterError
import velociraptor.autoplotter.plot as plot

from unyt import unyt_quantity, unyt_array
from yaml import safe_load
from typing import Union, List, Dict

from os import path, mkdir
from functools import reduce


class VelociraptorPlot(object):
    """
    Object representing a single figure of x against y.
    """

    # Forward declarations
    # variable to plot on the x-axis
    x: str
    # variable to plot on the y-axis
    y: str
    # log the x/y axes?
    x_log: bool
    y_log: bool
    # Units for x/y
    x_units: unyt_quantity
    y_units: unyt_quantity
    # Plot limits for x/y
    x_lim: List[Union[unyt_quantity, None]]
    y_lim: List[Union[unyt_quantity, None]]
    # override the axes?
    x_label_override: Union[None, str]
    y_label_override: Union[None, str]
    # plot median/mean line and give it properties
    mean_line: Union[None, VelociraptorLine]
    median_line: Union[None, VelociraptorLine]

    def __init__(self, filename: str, data: Dict[str, Union[Dict, str]]):
        """
        Initialise the plot object variables.
        """
        self.filename = filename
        self.data = data

        self._parse_data()

        return

    def _parse_data(self):
        """
        Parse the data and set defaults if not present.
        """

        try:
            self.x = self.data["x"]["quantity"]
            self.x_units = unyt_quantity(1.0, units=self.data["x"]["units"])
        except KeyError:
            raise AutoPlotterError(
                f"You must provide an x-quantity and units to plot for {self.filename}"
            )

        try:
            self.y = self.data["y"]["quantity"]
            self.y_units = unyt_quantity(1.0, units=self.data["y"]["units"])
        except KeyError:
            raise AutoPlotterError(
                f"You must provide an y-quantity and units to plot for {self.filename}"
            )

        self.x_lim = [None, None]

        try:
            self.x_lim[0] = unyt_quantity(
                float(self.data["x"]["start"]), units=self.data["x"]["units"]
            )
        except KeyError:
            pass

        try:
            self.x_lim[1] = unyt_quantity(
                float(self.data["x"]["end"]), units=self.data["x"]["units"]
            )
        except KeyError:
            pass

        self.y_lim = [None, None]

        try:
            self.y_lim[0] = unyt_quantity(
                float(self.data["y"]["start"]), units=self.data["y"]["units"]
            )
        except KeyError:
            pass

        try:
            self.y_lim[1] = unyt_quantity(
                float(self.data["y"]["end"]), units=self.data["y"]["units"]
            )
        except KeyError:
            pass

        try:
            self.x_log = bool(self.data["x"]["log"])
        except KeyError:
            self.x_log = True

        try:
            self.y_log = bool(self.data["y"]["log"])
        except KeyError:
            self.y_log = True

        try:
            self.x_label_override = self.data["x"]["label_override"]
        except KeyError:
            self.x_label_override = None

        try:
            self.y_label_override = self.data["y"]["label_override"]
        except KeyError:
            self.y_label_override = None

        try:
            self.median_line = VelociraptorLine("median", self.data["median"])
        except KeyError:
            self.median_line = None

        try:
            self.mean_line = VelociraptorLine("mean", self.data["mean"])
        except KeyError:
            self.mean_line = None

        return

    def make_plot(
        self, catalogue: VelociraptorCatalogue, directory: str, file_extension: str
    ):
        """
        Creates a plot using the given catalogue and the data that
        we have available.
        """

        x = reduce(getattr, self.x.split("."), catalogue)
        x.convert_to_units(self.x_units)
        y = reduce(getattr, self.y.split("."), catalogue)
        y.convert_to_units(self.y_units)

        fig, ax = plot.scatter_x_against_y(x, y)
        plot.decorate_axes(ax=ax, catalogue=catalogue)

        if self.x_log:
            ax.set_xscale("log")
        if self.y_log:
            ax.set_yscale("log")

        ax.set_xlim(*self.x_lim)
        ax.set_ylim(*self.y_lim)

        if self.median_line is not None:
            self.median_line.plot_line(ax=ax, x=x, y=y, label="Median")
        if self.mean_line is not None:
            self.mean_line.plot_line(ax=ax, x=x, y=y, label="Mean")

        fig.tight_layout()
        fig.savefig(f"{directory}/{self.filename}.{file_extension}")

        return


class AutoPlotter(object):
    """
    Main autoplotter object; contains all of the VelociraptorPlot objects
    and parsing code to turn the input yaml file into those.
    """

    # Forward declarations
    catalogue: VelociraptorCatalogue
    yaml: Dict[str, Union[Dict, str]]
    plots: List[VelociraptorPlot]

    def __init__(self, filename: str) -> None:
        """
        Initialises the AutoPlotter object with the yaml filename.
        """

        self.filename = filename
        self.load_yaml()
        self.parse_yaml()

        return

    def load_yaml(self):
        """
        Loads the yaml data from file.
        """

        with open(self.filename, "r") as handle:
            self.yaml = safe_load(handle)

        return

    def parse_yaml(self):
        """
        Parse the contents of the given yaml file into a list of
        VelociraptorPlot instances (self.plots).
        """

        self.plots = [
            VelociraptorPlot(filename, plot) for filename, plot in self.yaml.items()
        ]

        return

    def link_catalogue(self, catalogue: VelociraptorCatalogue):
        """
        Links a catalogue with this object so that the plots
        can actually be created.
        """

        self.catalogue = catalogue

        return

    def create_plots(self, directory: str, file_extension: str = "pdf"):
        """
        Creates and saves the plots in a directory.
        """

        # Try to create the directory
        if not path.exists(directory):
            mkdir(directory)

        for plot in self.plots:
            plot.make_plot(
                catalogue=self.catalogue,
                directory=directory,
                file_extension=file_extension,
            )

        return

