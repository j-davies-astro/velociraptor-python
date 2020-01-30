"""
The velociraptor module. 

More information is available in the documnetation.
"""

# First things first, we need to upgrade msun from a symbol to a
# first-class unit.
import unyt

try:
    unyt.define_unit("msun", unyt.msun, tex_repr=r"M_\odot")
except RuntimeError:
    # We've already done that, oops.
    pass

from velociraptor.catalogue.catalogue import VelociraptorCatalogue
from velociraptor.__version__ import __version__

from typing import Union


def load(
    filename: str, registration_file_path: Union[str, None] = None
) -> VelociraptorCatalogue:
    """
    Loads a velociraptor catalogue, producing a VelociraptorCatalogue
    object.

    Parameters
    ----------

    filename: str
        The filename of your VELOCIraptor catalogue file (i.e.
        the path to the .properties file).

    registration_file_path: str, optional
        The filename of the derived quantities script to register
        additional properties with the catalogue. This is an
        advanced feature. See the documentation for more details.


    Returns
    -------

    VelociraptorCatalogue
        The VelociraptorCatalogue object that describes your
        .properties file.
    """

    catalogue = VelociraptorCatalogue(filename)

    if registration_file_path is not None:
        catalogue.register_derived_quantities(registration_file_path)

    return catalogue
