"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

import h5py
import unyt

import numpy as np

from typing import Union, Callable, List

from velociraptor.units import VelociraptorUnits
from velociraptor.registration import global_registration_functions
from velociraptor.exceptions import RegistrationDoesNotMatchError


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
                    field_path=self.path, unit_system=self.units
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


def generate_catalogue(
    filename, extra_registration_functions: Union[None, List[Callable]] = None
):
    """
    Generates a catalogue object with the correct properties set.
    This is required as we can add properties to a class, but _not_
    to an object dynamically.

    So, here, we initialise the metadata, create a _copy_ of the
    __VelociraptorCatlaogue class, and then add all of our properties
    to that _class_ before instantiating it with the metadata.

    This is thanks to the very helpful StackOverflow answer here:
    https://stackoverflow.com/questions/1325673/how-to-add-property-to-a-class-dynamically    
    """

    # This creates a _copy_ of the _class_, not object.
    ThisCatalogue = type(
        "DynamicVelociraptorCatalogue",
        __VelociraptorCatalogue.__bases__,
        dict(__VelociraptorCatalogue.__dict__),
    )

    # We need two things to continue: the complete list of registration
    # functions, and the units.
    units = VelociraptorUnits(filename)

    if extra_registration_functions is not None:
        registration_functions = (
            extra_registration_functions + global_registration_functions
        )
    else:
        registration_functions = global_registration_functions

    # Using our full list of registration functions we can
    # find all of the valid datasets:

    # First load all field names from the HDF5 file so that they can be parsed.
    with h5py.File(filename, "r") as handle:
        field_paths = list(handle.keys())

    # Now build metadata:
    valid_field_metadata = []
    invalid_field_paths = []

    for path in field_paths:
        metadata = VelociraptorFieldMetadata(
            filename, path, registration_functions, units
        )

        if metadata.valid:
            valid_field_metadata.append(metadata)
        else:
            invalid_field_paths.append(path)

    # Now we can generate our local datasets for the valid paths.
    for metadata in valid_field_metadata:
        # First set our fake objects internally to none
        setattr(ThisCatalogue, f"_{metadata.snake_case}", None)

        # Now set the getters, setters, and deleters.
        setattr(
            ThisCatalogue,
            metadata.snake_case,
            property(
                generate_getter(
                    filename, metadata.snake_case, metadata.path, metadata.unit
                ),
                generate_setter(metadata.snake_case),
                generate_deleter(metadata.snake_case),
            ),
        )

    # Finally, we can actually create an instance of our new class.
    catalogue = ThisCatalogue(
        filename=filename,
        registration_functions=registration_functions,
        units=units,
        valid_field_metadata=valid_field_metadata,
        invalid_field_paths=invalid_field_paths,
    )

    return catalogue


class __VelociraptorCatalogue(object):
    """
    A velociraptor dataset, containing information that has correct units
    and are easily accessible through snake_case names.
    """

    def __init__(
        self,
        filename,
        registration_functions: Union[None, List[Callable]],
        units: VelociraptorUnits,
        valid_field_metadata: Union[List[VelociraptorFieldMetadata], None],
        invalid_field_paths: Union[List[str], None],
    ):
        """
        Initialise the velociraptor catalogue with all of the available
        datasets. This class should never be instantiated manually and should
        always be handled through the generate_catalogue function.

        Parameters:
        
        + filename: the filename of the catalogue
        + registration_functions: the full list of registration functions used for
                                  this catalogue
        + units: the corresponding VelociraptorUnits instance
        + valid_field_metadata: a list of VelociraptorFieldMetadata that correspond
                                to the valid fields found within the file
        + invalid_field_paths: a list of strings corresponding to invalid field
                               paths within the velociraptor catalogue.
        """
        self.filename = filename
        self.registration_functions = registration_functions
        self.units = units
        self.valid_field_metadata = valid_field_metadata
        self.invalid_field_paths = invalid_field_paths

        self.extract_properties_from_units()

        return

    def __str__(self):
        """
        Prints out some more useful information, rather than just
        the memory location.
        """

        return f"Velociraptor catalogue at {self.filename}."

    def extract_properties_from_units(self):
        """
        Use the self.units object to extract interesting parameters
        that should be visible from the top-level.
        """

        # Register some properties from the units that may be useful outside
        properties = ["a", "scale_factor", "z", "redshift"]

        for property in properties:
            setattr(self, property, getattr(self.units, property))

        return

