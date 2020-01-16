"""
Objects for observational data plotting.

Tools for adding in extra (e.g. observational) data to plots.

Includes an object container and helper functions for creating
and reading files.
"""

from unyt import unyt_quantity, unyt_array
from matplotlib.pyplot import Axes

from astropy.units import Quantity
from astropy.cosmology.core import Cosmology
from astropy.cosmology import wCDM, FlatLambdaCDM

import h5py
import json

from typing import Union


def save_cosmology(handle: h5py.File, cosmology: Cosmology):
    """
    Save the (astropy) cosmology to a HDF5 dataset.
    """
    group = handle.create_group("cosmology").attrs

    group.create("H0", cosmology.H0)
    group.create("Om0", cosmology.Om0)
    group.create("Ode0", cosmology.Ode0)
    group.create("Tcmb0", cosmology.Tcmb0)
    group.create("Neff", cosmology.Neff)
    group.create("m_nu", cosmology.m_nu)
    group.create("m_nu_units", str(cosmology.m_nu.unit))
    group.create("Ob0", cosmology.Ob0)
    group.create("name", cosmology.name)

    try:
        group.create("w0", cosmology.w0)
    except:
        # No EoS!
        pass

    return


def load_cosmology(handle: h5py.File):
    """
    Save the (astropy) cosmology to a HDF5 dataset.
    """
    group = handle["cosmology"].attrs

    try:
        cosmology = wCDM(
            H0=group["H0"],
            Om0=group["Om0"],
            Ode0=group["Ode0"],
            w0=group["w0"],
            Tcmb0=group["Tcmb0"],
            Neff=group["Neff"],
            m_nu=Quantity(group["m_nu"], unit=group["m_nu_units"]),
            Ob0=group["Ob0"],
            name=group["name"],
        )
    except KeyError:
        # No EoS
        cosmology = FlatLambdaCDM(
            H0=group["H0"],
            Om0=group["Om0"],
            Tcmb0=group["Tcmb0"],
            Neff=group["Neff"],
            m_nu=Quantity(group["m_nu"], unit=group["m_nu_units"]),
            Ob0=group["Ob0"],
            name=group["name"],
        )

    return cosmology


class ObservationalData(object):
    """
    Observational data object. Contains routines
    for both writing and reading HDF5 files containing
    the observations, as well as plotting.
    """

    # Data stored in this object
    # name of the observation (to be plotted on axes)
    name: str
    # units for axes
    x_units: unyt_quantity
    y_units: unyt_quantity
    # data for axes
    x: unyt_array
    y: unyt_array
    # scatter
    x_scatter: Union[unyt_array, None]
    y_scatter: Union[unyt_array, None]
    # x and y are comoving?
    x_comoving: bool
    y_comoving: bool
    # x and y labels
    x_description: str
    y_description: str
    # filename to read from or write to
    filename: str
    # free-text comment describing data
    comment: str
    # citation for data
    citation: str
    bibcode: str
    # redshift that the data is at
    redshift: float
    # plot as points, or a line?
    plot_as: Union[str, None] = None
    # the cosmology that this dataset was corrected to
    cosmology: Cosmology

    def __init__(self):
        """
        Initialises the object for observational data. Does nothing as we are
        unsure if we wish to read or write data at this point.
        """

        return

    def load(self, filename: str):
        """
        Loads the observations from file.
        """

        self.filename = filename

        # Load data here.
        self.x = unyt_array.from_hdf5(filename, dataset_name="values", group_name="x")
        self.y = unyt_array.from_hdf5(filename, dataset_name="values", group_name="y")
        self.x_units = self.x.units
        self.y_units = self.y.units

        try:
            self.x_scatter = unyt_array.from_hdf5(
                filename, dataset_name="scatter", group_name="x"
            )
        except KeyError:
            self.x_scatter = None

        try:
            self.y_scatter = unyt_array.from_hdf5(
                filename, dataset_name="scatter", group_name="y"
            )
        except KeyError:
            self.y_scatter = None

        with h5py.File(filename, "r") as handle:
            metadata = handle["metadata"].attrs

            self.comment = metadata["comment"]
            self.name = metadata["name"]
            self.citation = metadata["citation"]
            self.bibcode = metadata["bibcode"]
            self.redshift = metadata["redshift"]
            self.plot_as = metadata["plot_as"]

            self.x_comoving = bool(handle["x"].attrs["comoving"])
            self.y_comoving = bool(handle["y"].attrs["comoving"])
            self.y_description = str(handle["y"].attrs["description"])
            self.x_description = str(handle["x"].attrs["description"])

            self.cosmology = load_cosmology(handle)

        return

    def write(self, filename: str):
        """
        Writes the observations to file.
        """

        self.filename = filename

        # Write data here
        self.x.write_hdf5(filename, dataset_name="values", group_name="x")
        self.y.write_hdf5(filename, dataset_name="values", group_name="y")

        if self.x_scatter is not None:
            self.x_scatter.write_hdf5(filename, dataset_name="scatter", group_name="x")

        if self.y_scatter is not None:
            self.y_scatter.write_hdf5(filename, dataset_name="scatter", group_name="y")

        with h5py.File(filename, "a") as handle:
            metadata = handle.create_group("metadata").attrs

            metadata.create("comment", self.comment)
            metadata.create("name", self.name)
            metadata.create("citation", self.citation)
            metadata.create("bibcode", self.bibcode)
            metadata.create("redshift", self.redshift)
            metadata.create("plot_as", self.plot_as)

            handle["x"].attrs.create("comoving", self.x_comoving)
            handle["y"].attrs.create("comoving", self.y_comoving)
            handle["x"].attrs.create("description", self.x_description)
            handle["y"].attrs.create("description", self.y_description)

            save_cosmology(handle=handle, cosmology=self.cosmology)

        return

    def associate_x(
        self,
        array: unyt_array,
        scatter: Union[unyt_array, None],
        comoving: bool,
        description: str,
    ):
        """
        Associate an x quantity with this observational data instance.
        """

        self.x = array
        self.x_units = array.units
        self.x_comoving = comoving
        self.x_description = description

        if scatter is not None:
            self.x_scatter = scatter.to(self.x_units)
        else:
            self.x_scatter = None

        return

    def associate_y(
        self,
        array: unyt_array,
        scatter: Union[unyt_array, None],
        comoving: bool,
        description: str,
    ):
        """
        Associate an y quantity with this observational data instance.
        """

        self.y = array
        self.y_units = array.units
        self.y_comoving = comoving
        self.y_description = description

        if scatter is not None:
            self.y_scatter = scatter.to(self.y_units)
        else:
            self.y_scatter = None

        return

    def associate_citation(self, citation: str, bibcode: str):
        """
        Associate a citation with this observational data instance.
        """

        self.citation = citation
        self.bibcode = bibcode

        return

    def associate_name(self, name: str):
        """
        Associate a name with this observational data instance.
        """

        self.name = name

        return

    def associate_comment(self, comment: str):
        """
        Associate a comment with this observational data instance.
        """

        self.comment = comment

        return

    def associate_redshift(self, redshift: float):
        """
        Associate the redshift that the observations were taken at
        with this observational data instance.
        """

        self.redshift = redshift

        return

    def associate_plot_as(self, plot_as: str):
        """
        Associate the 'plot_as' field - this should either be line
        or points.
        """

        if plot_as not in ["line", "points"]:
            raise Exception("Please supply plot_as as either points or line.")

        self.plot_as = plot_as

        return

    def associate_cosmology(self, cosmology: Cosmology):
        """
        Associate a cosmology with this dataset that it has been corrected for.
        This should be an astropy cosmology instance.
        """

        self.cosmology = cosmology

        return

    def plot_on_axes(self, axes: Axes, errorbar_kwargs: Union[dict, None] = None):
        """
        Plot this set of observational data as an errorbar().
        """

        # Do this because dictionaries are mutable
        if errorbar_kwargs is not None:
            kwargs = errorbar_kwargs
        else:
            kwargs = {}

        # Ensure correct units throughout, in case somebody chagned them
        if self.x_scatter is not None:
            self.x_scatter.convert_to_units(self.x.units)

        if self.y_scatter is not None:
            self.y_scatter.convert_to_units(self.y.units)

        if self.plot_as == "points":
            kwargs["linestyle"] = "none"
            kwargs["marker"] = "."

        axes.errorbar(
            self.x,
            self.y,
            yerr=self.y_scatter,
            xerr=self.x_scatter,
            **kwargs,
            label=self.citation
        )

        return
