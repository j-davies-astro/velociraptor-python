import numpy as np
import h5py
import unyt

from typing import List, Set
from types import SimpleNamespace

from velociraptor.catalogue.catalogue import Catalogue
from velociraptor.catalogue.translator import VR_to_SOAP

from functools import reduce

from astropy.cosmology import wCDM, FlatLambdaCDM
import unyt

from typing import Union
from abc import ABC, abstractmethod
from pathlib import Path


class CatalogueElement(object):
    """
    Abstract class for catalogue elements. These map to specific objects in
    the SOAP output file.

    The SOAP output file is a tree structure with HDF5 groups that contain
    either more HDF5 groups or HDF5 datasets. Each group/dataset has a name
    that corresponds to its path in the SOAP file.
    """

    # path to the SOAP file
    file_name: Path
    # name of the HDF5 group/dataset in the SOAP file
    name: str

    def __init__(self, file_name: Path, name: str):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
         - name: str
           Path of the dataset/group in the SOAP catalogue file.
        """
        self.file_name = file_name
        self.name = name


class CatalogueDataset(CatalogueElement):
    """
    Representation of a SOAP dataset.

    A dataset has unit metadata and values that are only read if the dataset
    is actually used.
    """

    # conversion factor from SOAP units to a unyt_array with units
    conversion_factor: Union[unyt.unyt_quantity, None]
    # value of the dataset. Only set when the dataset is actually used
    _value: Union[unyt.unyt_array, None]

    def __init__(self, file_name: Path, name: str, handle: h5py.File):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
         - name: str
           Path of the dataset in the SOAP catalogue file.
         - handle: h5py.File
           HDF5 file handle. Used to avoid having to open and close the file
           in the constructor.
        """
        super().__init__(file_name, name)

        self._value = None
        self.conversion_factor = None
        self._register_metadata(handle)

    def _register_metadata(self, handle: h5py.File):
        """
        Read the unit metadata from the HDF5 file and store it in the conversion
        factor.

        Parameters:
         - handle: h5py.File
           HDF5 file handle. Used to avoid having to open and close the file
           in the constructor.
        """
        metadata = handle[self.name].attrs
        factor = (
            metadata["Conversion factor to CGS (including cosmological corrections)"][0]
            * unyt.A ** metadata["U_I exponent"][0]
            * unyt.cm ** metadata["U_L exponent"][0]
            * unyt.g ** metadata["U_M exponent"][0]
            * unyt.K ** metadata["U_T exponent"][0]
            * unyt.s ** metadata["U_t exponent"][0]
        )
        self.conversion_factor = unyt.unyt_quantity(factor)
        # avoid overflow by setting the base unit system to something that works
        # well for cosmological simulations
        self.conversion_factor.convert_to_base("galactic")

    def set_value(self, value: unyt.unyt_array, group: CatalogueGroup):
        """
        Setter for the dataset values.

        Parameters:
         - value: unyt.unyt_array
           New values for the dataset.
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).
        """
        self._value = value

    def del_value(self, group: CatalogueGroup):
        """
        Deleter for the dataset values.

        Parameters:
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).
        """
        del self._value
        self._value = None

    def get_value(self, group: CatalogueGroup) -> unyt.unyt_array:
        """
        Getter for the dataset values.
        Performs lazy reading: if the value has not been read before, it is
        read from the SOAP catalogue file. Otherwise, a buffered value is used.

        Parameters:
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).

        Returns the dataset values as a unyt.unyt_array.
        """
        if self._value is None:
            with h5py.File(self.file_name, "r") as handle:
                self._value = handle[self.name][:] * self.conversion_factor
            self._value.name = self.name.replace("/", " ").replace("_", "").strip()
        return self._value


class CatalogueDerivedDataset(CatalogueElement, ABC):

    terms: List[CatalogueDataset]

    def __init__(self, file_name, name, terms):
        super().__init__(file_name, name)
        self._value = None
        self.terms = list(terms)

    def set_value(self, value, group):
        self._value = value

    def del_value(self, group):
        del self._value
        self._value = None

    def get_value(self, group):
        if self._value is None:
            values = [term.get_value(group) for term in self.terms]
            self._value = self.compute_value(*values)
        return self._value

    @abstractmethod
    def compute_value(self, *values):
        raise NotImplementedError("This calculation has not been implemented!")


class VelocityDispersion(CatalogueDerivedDataset):
    def compute_value(self, velocity_dispersion_matrix):
        return np.sqrt(velocity_dispersion_matrix[:, 0:2].sum(axis=1))


class CatalogueGroup(CatalogueElement):

    elements: List[CatalogueElement]

    def __init__(self, file_name, name, handle):
        super().__init__(file_name, name)

        self.elements = []
        self._register_elements(handle)
        self._register_properties()
        self._register_extra_properties()

    def _register_elements(self, handle):
        h5group = handle[self.name] if self.name != None else handle["/"]
        for (key, h5obj) in h5group.items():
            if isinstance(h5obj, h5py.Group):
                el = CatalogueGroup(self.file_name, f"{self.name}/{key}", handle)
                dynamically_register_properties(el)
                self.elements.append(el)
            elif isinstance(h5obj, h5py.Dataset):
                self.elements.append(
                    CatalogueDataset(self.file_name, f"{self.name}/{key}", handle)
                )

    def __str__(self):
        return f"CatalogueGroup containing the following elements: {[el.name for el in self.elements]}"

    def _register_properties(self):
        self.properties = {}
        for el in self.elements:
            basename = el.name.split("/")[-1].lower()
            # attribute names cannot start with a number
            if basename[0].isnumeric():
                basename = f"v{basename}"
            if isinstance(el, CatalogueGroup):
                setattr(self, basename, el)
            elif isinstance(el, CatalogueDataset):
                self.properties[basename] = (
                    el,
                    property(el.get_value, el.set_value, el.del_value),
                )

    def _register_extra_properties(self):
        """
        Register derived properties that were present in the old VR catalogue
        but not in the SOAP catalogue.
        These could also use registration functions, but that would affect the
        pipeline.

        In practice, the only property that needs this special treatment is
        'stellarvelocitydispersion'. The reason is that SOAP contains the full
        velocity dispersion matrix, while VR only outputs the square root of
        the trace of this matrix, which is the quantity that is used in the
        pipeline.
        """
        try:
            stellar_velocity_dispersion_matrix = self.properties[
                "stellarvelocitydispersionmatrix"
            ][0]
            el = VelocityDispersion(
                self.file_name,
                "stellarvelocitydispersion",
                [stellar_velocity_dispersion_matrix],
            )
            self.elements.append(el)
            self.properties["stellarvelocitydispersion"] = (
                el,
                property(el.get_value, el.set_value, el.del_value),
            )
        except KeyError:
            pass


def dynamically_register_properties(group: CatalogueGroup):
    """
    Absolute magic: trick an object into thinking it is of a different class
    that has additional properties. Surprisingly, this works like a charm.
    """

    class_name = f"{group.__class__.__name__}{group.name.replace('/', '_')}"
    props = {name: value[1] for (name, value) in group.properties.items()}
    child_class = type(class_name, (group.__class__,), props)

    group.__class__ = child_class


class SOAPCatalogue(Catalogue):

    file_name: str
    root: CatalogueGroup
    names_used: Set[str]

    def __init__(self, file_name):
        super().__init__("SOAP")
        self.file_name = file_name
        self.names_used = set()
        self._register_quantities()

    def print_fields(self):
        print("SOAP catalogue fields used:")
        for name in self.names_used:
            print(f"  {name}")

    def _register_quantities(self):
        with h5py.File(self.file_name, "r") as handle:
            self.root = CatalogueGroup(self.file_name, None, handle)
            cosmology = handle["SWIFT/Cosmology"].attrs
            # set up a dummy units object for compatibility with the old VR API
            self.units = SimpleNamespace()
            self.a = cosmology["Scale-factor"][0]
            self.units.scale_factor = cosmology["Scale-factor"][0]
            self.z = cosmology["Redshift"][0]
            self.units.redshift = cosmology["Redshift"][0]
            H0 = cosmology["H0 [internal units]"][0]
            Omega_m = cosmology["Omega_m"][0]
            Omega_lambda = cosmology["Omega_lambda"][0]
            w0 = cosmology["w_0"][0]
            Omega_b = cosmology["Omega_b"][0]
            if w0 != -1.0:
                self.cosmology = wCDM(
                    H0=H0, Om0=Omega_m, Ode0=Omega_DE, w0=w_of_DE, Ob0=Omega_b
                )
            else:
                # No EoS
                self.cosmology = FlatLambdaCDM(H0=H0, Om0=Omega_m, Ob0=Omega_b)
            # get the box size and length unit from the SWIFT header and unit metadata
            boxsize = handle["SWIFT/Header"].attrs["BoxSize"][0]
            boxsize_unit = (
                handle["SWIFT/InternalCodeUnits"].attrs["Unit length in cgs (U_L)"]
                * unyt.cm
            ).in_base("galactic")
            boxsize *= boxsize_unit
            physical_boxsize = self.a * boxsize
            self.units.box_length = boxsize
            self.units.comoving_box_volume = boxsize ** 3
            self.units.period = physical_boxsize
            self.units.physical_box_volume = physical_boxsize ** 3
            self.units.cosmology = self.cosmology

    def get_SOAP_quantity(self, quantity_name):
        path = [
            f"v{path_part}" if path_part[0].isnumeric() else path_part
            for path_part in quantity_name.split(".")
        ]
        value = reduce(getattr, path, self.root)
        self.names_used.add(quantity_name)
        return value

    def get_quantity(self, quantity_name):
        try:
            return super().get_quantity(quantity_name)
        except AttributeError:
            pass
        try:
            return self.get_SOAP_quantity(quantity_name)
        except AttributeError:
            pass
        try:
            SOAP_quantity_name, colidx = VR_to_SOAP(quantity_name)
            quantity = self.get_SOAP_quantity(SOAP_quantity_name)
            if colidx >= 0:
                return quantity[:, colidx]
            else:
                return quantity
        except NotImplementedError as err:
            if quantity_name in [
                "apertures.veldisp_star_10_kpc",
                "apertures.veldisp_star_30_kpc",
            ]:
                print(f"Ignoring missing {quantity_name}...")
                return None
            raise err
