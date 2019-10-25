"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

import h5py
import unyt

import numpy as np

from typing import Union, Callable, List

from velociraptor.registration import global_registration_functions
from velociraptor.exceptions import RegistrationDoesNotMatchError


class VelociraptorUnits(object):
    """
    Generates a unyt system that can then be used with the velociraptor data.

    You are probably looking for the following attributes:

    + VelociraptorUnits.length
    + VelociraptorUnits.mass
    + VelociraptorUnits.metallicity (relative to solar)
    + VelociraptorUnits.age
    + VelociraptorUnits.velocity
    + VelociraptorUnits.star_formation_rate

    This will allow you to extract variables in the correct units. This object
    also holds the current scale factor and redshift through the a and z variables.
    Finally, it contains whether or not the current unit system is comoving
    (VelociraptorUnits.comoving) and whether or not the underlying simulation
    was cosmological (VelociraptorUnits.cosmological).
    """

    def __init__(self, filename):
        self.filename = filename

        self.get_unit_dictionary()

        return

    def get_unit_dictionary(self):
        """
        Gets the unit library from the header information in the file.
        These are a mix of units, so we just read them all -- and allow the
        people who define the registration functions to figure out how to
        use them.
        """

        self.units = {}

        with h5py.File(self.filename, "r") as handle:
            attributes = handle.attrs

            self.units["length"] = attributes["Length_unit_to_kpc"] * unyt.kpc
            self.units["mass"] = attributes["Mass_unit_to_solarmass"] * unyt.msun
            self.units["metallicity"] = attributes["Metallicity_unit_to_solar"]
            self.units["age"] = attributes["Stellar_age_unit_to_yr"] * unyt.year
            self.units["velocity"] = attributes["Velocity_to_kms"] * unyt.km / unyt.s
            self.units["star_formation_rate"] = (
                attributes["SFR_unit_to_solarmassperyear"] * unyt.msun / unyt.year
            )

            self.scale_factor = attributes["Time"]
            self.a = self.scale_factor
            self.redshift = 1.0 / self.a - 1.0
            self.z = self.redshift

            self.cosmological = bool(attributes["Cosmological_Sim"])
            self.comoving = bool(attributes["Comoving_or_Physical"])

        # Unpack the dictionary to variables
        for name, unit in self.units.items():
            setattr(self, name, unit)

        return


class VelociraptorFieldMetadata(object):
    """
    Metadata for a velociraptor field. Pass it a field path and a filename,
    and it will:

    + Use the registration functions to find the correct units and
      "fancy name".
    + Assign a proper snake_case_name to the dataset.
    """

    # Forward declarations for the field.

    # Is this a valid field?
    valid: bool = False
    # The fancy name of this field for plotting, provided by registration function
    name: str = ""
    # The snake case name of this field for use accessing the object.
    snake_case: str = ""
    # The unit of this field
    unit: str = ""
    # The registartion function that matched with this field
    corresponding_registration_function: Union[Callable, None] = None

    def __init__(
        self,
        filename,
        path: str,
        registration_functions: List[Callable],
        units: VelociraptorUnits,
    ):
        """
        I take in:

        + filename of the velociraptor properties file
        + path of the field you wish me to look at
        + registration_functions a list of callables with the registration
          function signature (see registration.py or the documentation)
        + units, a pointer or copy of the unit system associated with this file.
        """

        # Filename not currently used but may be required later on if
        # actual field metadata is included in the velociraptor properties files
        self.filename = filename
        self.path = path
        self.registration_functions = registration_functions
        self.units = units

        self.register_field_properties()

        return

    def register_field_properties(self):
        """
        Registers the field properties using the registration functions.
        """

        for reg in self.registration_functions:
            try:
                self.unit, self.name, self.snake_case = reg(
                    field_path=self.path, units=self.units
                )
                self.valid = True
                self.corresponding_registration_function = reg
            except RegistrationDoesNotMatchError:
                continue

        return


def generate_getter(filename, name: str, field: str, unit):
    """
    Generates a function that:

    a) If self._`name` exists, return it
    b) If not, open `filename`
    c) Reads filename[`field`]
    d) Set self._`name`
    e) Return self._`name`.
    """

    def getter(self):
        current_value = getattr(self, f"_{name}")

        if current_value is not None:
            return current_value
        else:
            with h5py.File(filename, "r") as handle:
                try:
                    setattr(self, f"_{name}", unyt.unyt_array(handle[field][...], unit))
                except KeyError:
                    print(f"Could not read {field}")
                    return None

        return getattr(self, f"_{name}")

    return getter


def generate_setter(name: str):
    """
    Generates a function that sets self._name to the value that is passed to it.
    """

    def setter(self, value):
        setattr(self, f"_{name}", value)

        return

    return setter


def generate_deleter(name: str):
    """
    Generates a function that destroys self._name (sets it back to None).
    """

    def deleter(self):
        current_value = getattr(self, f"_{name}")
        del current_value
        setattr(self, f"_{name}", None)

        return

    return deleter


class VelociraptorCatalogue(object):
    """
    A velociraptor dataset, containing information that has correct units
    and are easily accessible through snake_case names.
    """

    # Pre-set some variables

    # List of registration functions that we will use.
    registration_functions: Union[None, List[Callable]] = None

    def __init__(
        self, filename, extra_registration_functions: Union[None, List[Callable]] = None
    ):
        """
        Initialise the velociraptor catalogue with all of the available
        datasets.

        If you have added custom properties to your velociraptor catalogue,
        you can add registration functions for these here by supplying a list
        of them to extra_registartion_functions.
        """
        self.filename = filename

        self.set_registration_functions(extra_registration_functions)
        self.get_units()
        self.create_field_datasets()

        return

    def __str__(self):
        """
        Prints out some more useful information, rather than just
        the memory location.
        """

        return f"Velociraptor catalogue at {self.filename}."

    def set_registration_functions(
        self, extra_registration_functions: Union[None, List[Callable]]
    ):
        """
        Sets the self.registration_functions variable.
        """

        if extra_registration_functions is not None:
            self.registration_functions = (
                extra_registration_functions + global_registration_functions
            )
        else:
            self.registration_functions = global_registration_functions

        return

    def get_units(self):
        """
        Loads the units from the velociraptor catalogue. This happens automatically,
        but you can call this function again if you mess things up.
        """

        self.units = VelociraptorUnits(self.filename)

        # Register some properties from the units that may be useful outside
        properties = ["a", "scale_factor", "z", "redshift"]

        for property in properties:
            setattr(self, property, getattr(self.units, property))

        return

    def create_field_datasets(self):
        """
        Creates field datasets for all valid datasets in the file. We also
        store a separate list of invalid datasets that we could not correctly
        parse.
        """

        if not hasattr(self, "units"):
            self.get_units()

        # First load all field names from the HDF5 file so that they can be parsed.
        with h5py.File(self.filename, "r") as handle:
            self.field_paths = list(handle.keys())

        # Now build metadata:

        self.valid_field_metadata = []
        self.invalid_field_paths = []

        for path in self.field_paths:
            metadata = VelociraptorFieldMetadata(
                self.filename, path, self.registration_functions, self.units
            )

            if metadata.valid:
                self.valid_field_metadata.append(metadata)
            else:
                self.invalid_field_paths.append(path)

        # Now we can generate our local datasets for the valid paths.
        for metadata in self.valid_field_metadata:
            setattr(
                self,
                metadata.snake_case,
                property(
                    generate_getter(
                        self.filename,
                        metadata.snake_case,
                        metadata.field,
                        metadata.unit,
                    ),
                    generate_setter(metadata.snake_case),
                    generate_deleter(metadata.snake_case),
                ),
            )

        return

