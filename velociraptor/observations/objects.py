"""
Objects for observational data plotting.

Tools for adding in extra (e.g. observational) data to plots.

Includes an object container and helper functions for creating
and reading files.
"""

from unyt import unyt_quantity, unyt_array
from numpy import tanh, log10
from matplotlib.pyplot import Axes
from matplotlib import rcParams

from astropy.units import Quantity
from astropy.cosmology.core import Cosmology
from astropy.cosmology import wCDM, FlatLambdaCDM

import h5py
import json

from typing import Union

# Default z_orders for errorbar points and lines
line_zorder = -5
points_zorder = -6


def save_cosmology(handle: h5py.File, cosmology: Cosmology):
    """
    Save the (astropy) cosmology to a HDF5 dataset.

    Parameters
    ----------

    handle: h5py.File
        h5py file handle to save the cosmology to. This is performed
        by creating a cosmology group and setting attributes.

    cosmology: astropy.cosmology.Cosmology
        The Astropy cosmology instance to save to the HDF5 file. This
        is performed by extracting all of the key variables and saving
        them as either floating point numbers or strings.

    Notes
    -----

    This process can be reversed by using load_cosmology.
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

    Parameters
    ----------

    handle: h5py.File
        h5py file handle to read the cosmology from.

    Returns
    -------

    astropy.cosmology.Cosmology:
        Astropy cosmology instance extracted from the HDF5 file.
    """

    try:
        group = handle["cosmology"].attrs
    except:
        return None

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

    Attributes
    ----------
    name: str
        Name of the observation for users to identifty

    x_units: unyt_quantity
        Units for horizontal axes

    y_units: unyt_quantity
        Units for vertical axes

    x: unyt_array
        Horizontal data points

    y: unyt_array
        Vertical data points

    x_scatter: Union[unyt_array, None]
        Scatter in horizontal direction. Can be None, or an
        unyt_array of shape 1XN (symmetric) or 2XN (non-symmetric)
        such that it can be passed to plt.errorbar easily.

    y_scatter: Union[unyt_array, None]
        Scatter in vertical direction. Can be None, or an
        unyt_array of shape 1XN (symmetric) or 2XN (non-symmetric)
        such that it can be passed to plt.errorbar easily.

    x_comoving: bool
        Whether or not the horizontal values are comoving (True)
        or physical (False)

    y_comoving: bool
        Whether or not the vertical values are comoving (True)
        or physical (False)

    x_description: str
        Default label for horizontal axis (without units), also a
        description of the variable.

    y_description: str
        Default label for horizontal axis (without units), also a
        description of the variable.

    filename: str
        Filename that the data was read from, or was written to.

    comment: str
        A free-text comment describing the data, including e.g.
        which cosmology and IMF it is calibrated to.

    citation: str
        Short citation for data, e.g. Author et al. (Year) (Project),
        such as Baldry et al. (2012) (GAMA)

    bibcode: str
        Bibcode for citation, this can be found on the NASA ADS.

    redshift: float
        Redshift at which the data is collected at. If a range, use
        the mid-point.

    plot_as: Union[str, None]
        Whether the data should be plotted as points (typical for observations)
        or as a line (typical for simulation data). Allowed values:

        + points
        + line

    cosmology: Cosmology
        Astropy cosmology that the data has been corrected to.
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


        Parameters
        ----------

        filename: str
            The filename to load the data from. Probably should end in
            .hdf5.
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

        Parameters
        ----------

        filename: str
            The filename to write the data to. Probably should end in
            .hdf5.
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

        Parameters
        ----------

        array: unyt_array
            The array of (horizontal) data points, including units.

        scatter: Union[unyt_array, None]
            The array of scatter (1XN or 2XN) in the horizontal
            co-ordinates with associated units.

        comoving: bool
            Whether or not the horizontal values are comoving.

        description: str
            Short description of the data, e.g. Stellar Masses
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

        Parameters
        ----------

        array: unyt_array
            The array of (vertical) data points, including units.

        scatter: Union[unyt_array, None]
            The array of scatter (1XN or 2XN) in the vertical
            co-ordinates with associated units.

        comoving: bool
            Whether or not the vertical values are comoving.

        description: str
            Short description of the data, e.g. Stellar Masses
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

        Parameters
        ----------

        citation: str
            Short citation, formatted as follows: Author et al. (Year) (Project),
            e.g. Baldry et al. (2012) (GAMA)

        bibcode: str
            Bibcode for the paper the data was extracted from, available
            from the NASA ADS or publisher. E.g. 2012MNRAS.421..621B
        """

        self.citation = citation
        self.bibcode = bibcode

        return

    def associate_name(self, name: str):
        """
        Associate a name with this observational data instance.
        
        Parameters
        ----------

        name: str
            Short name to describe the dataset.
        """

        self.name = name

        return

    def associate_comment(self, comment: str):
        """
        Associate a comment with this observational data instance.

        Parameters
        ----------

        comment: str
            A free-text comment describing the data, including e.g.
            which cosmology and IMF it is calibrated to.
        """

        self.comment = comment

        return

    def associate_redshift(self, redshift: float):
        """
        Associate the redshift that the observations were taken at
        with this observational data instance.

        Parameters
        ----------

        redshift: float
            Redshift at which the data is collected at. If a range, use
            the mid-point.

        """

        self.redshift = redshift

        return

    def associate_plot_as(self, plot_as: str):
        """
        Associate the 'plot_as' field - this should either be line
        or points.

        Parameters
        ----------

        plot_as: str
            Either points or line
        """

        if plot_as not in ["line", "points"]:
            raise Exception("Please supply plot_as as either points or line.")

        self.plot_as = plot_as

        return

    def associate_cosmology(self, cosmology: Cosmology):
        """
        Associate a cosmology with this dataset that it has been corrected for.
        This should be an astropy cosmology instance.

        Parameters
        ----------

        cosmology: astropy.cosmology.Cosmology
            Astropy cosmology instance describing what cosmology the data has
            been corrected to.
        """

        self.cosmology = cosmology

        return

    def plot_on_axes(self, axes: Axes, errorbar_kwargs: Union[dict, None] = None):
        """
        Plot this set of observational data as an errorbar().

        Parameters
        ----------

        axes: plt.Axes
            The matplotlib axes to plot the data on. This will either
            plot the data as a line or a set of errorbar points, with
            the short citation (self.citation) being included in the
            legend automatically.

        errorbar_kwargs: dict
            Optional keyword arguments to pass to plt.errorbar.
        """

        # Do this because dictionaries are mutable
        if errorbar_kwargs is not None:
            kwargs = errorbar_kwargs
        else:
            kwargs = {}

        # Ensure correct units throughout, in case somebody changed them
        if self.x_scatter is not None:
            self.x_scatter.convert_to_units(self.x.units)

        if self.y_scatter is not None:
            self.y_scatter.convert_to_units(self.y.units)

        if self.plot_as == "points":
            kwargs["linestyle"] = "none"
            kwargs["marker"] = "."
            kwargs["zorder"] = points_zorder

            # Need to "intelligently" size the markers
            kwargs["markersize"] = (
                rcParams["lines.markersize"]
                * (1.5 - tanh(2.0 * log10(len(self.x)) - 4.0))
                / 2.5
            )

            kwargs["alpha"] = (3.0 - tanh(2.0 * log10(len(self.x)) - 4.0)) / 4.0

            # Looks weird if errorbars are present
            if self.y_scatter is None:
                kwargs["markerfacecolor"] = "none"

            if len(self.x) > 1000:
                kwargs["rasterize"] = True
        elif self.plot_as == "line":
            kwargs["zorder"] = line_zorder

        try:
            # Make both the data name and redshift appear in the legend
            data_label = f"{self.citation} ($z={self.redshift:.cd ;1f}$)"
        except (TypeError, ValueError):
            data_label = self.citation

        axes.errorbar(
            self.x,
            self.y,
            yerr=self.y_scatter,
            xerr=self.x_scatter,
            **kwargs,
            label=data_label
        )

        return
