"""
All classes that are involved in the handling of the units, including
the master VelociraptorUnits class.
"""


import unyt
import h5py


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

    # Pre-define these for autocomplete.
    length: unyt.unyt_quantity
    mass: unyt.unyt_quantity
    metallicity: unyt.unyt_quantity
    age: unyt.unyt_quantity
    velocity: unyt.unyt_quantity
    star_formation_rate: unyt.unyt_quantity

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
            self.units["metallicity"] = (
                attributes["Metallicity_unit_to_solar"] * unyt.dimensionless
            )
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

