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


def load(filename):
    """
    Loads a velociraptor catalogue, producing a VelociraptorCatalogue
    object.
    """

    return VelociraptorCatalogue(filename)
