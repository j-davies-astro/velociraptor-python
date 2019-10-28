"""
Routines that provide translation of velociraptor quantities into something a
little more human readable, or to internal quantities.
"""

import unyt

from velociraptor.units import VelociraptorUnits


def typo_correct(particle_property_name: str):
    """
    Corrects for any typos in field names that may exist.
    """

    key = {"veldips": "veldisp"}

    if particle_property_name in key.keys():
        return key[particle_property_name]
    else:
        return particle_property_name


def get_aperture_unit(unit_name: str, unit_system: VelociraptorUnits):
    """
    Converts the velociraptor strings to internal velociraptor units 
    from the naming convention in the velociraptor files.
    """

    # Correct any typos
    corrected_name = typo_correct(unit_name)

    key = {
        "SFR": unit_system.star_formation_rate,
        "Zmet": unit_system.metallicity,
        "mass": unit_system.mass,
        "npart": unyt.dimensionless,
        "rhalfmass": unit_system.length,
        "veldisp": unit_system.velocity,
    }

    return key[corrected_name]


def get_particle_property_name_conversion(name: str, ptype: str):
    """
    Takes an internal velociraptor particle property and returns
    a fancier name for use in plot legends. Typically used for the
    complex aperture properties.
    """

    corrected_name = typo_correct(name)

    combined_name = f"{corrected_name}_{ptype}"

    key = {
        "SFR_": r"SFR $\dot{\rho}_*$",
        "SFR_gas": r"Gas SFR $\dot{\rho}_*$",
        "Zmet_": r"Metallicity $Z$",
        "Zmet_gas": r"Gas Metallicity $Z_{\rm g}$",
        "Zmet_star": r"Stellar Metallicity $Z_*$",
        "Zmet_bh": r"Black Hole Metallicity $Z_{\rm BH}$",
        "mass_": r"Mass $M$",
        "mass_gas": r"Gas Mass $M_{\rm g}$",
        "mass_star": r"Stellar Mass $M_*$",
        "mass_bh": r"Black Hole Mass $M_{\rm BH}$",
        "npart_": r"Number of Particles $N$",
        "npart_gas": r"Number of Gas Particles $N_{\rm g}$",
        "npart_star": r"Number of Stellar Particles $N_*$",
        "npart_bh": r"Black Hole Mass $N_{\rm BH}$",
        "rhalfmass_": r"Half-mass Radius $R_{50}$",
        "rhalfmass_gas": r"Gas Half-mass Radius $R_{50, {\rm g}}$",
        "rhalfmass_star": r"Stellar Half-mass Radius $R_{50, *}$",
        "rhalfmass_bh": r"Black Hole Half-mass Radius $R_{50, {\rm BH}}$",
        "veldisp_": r"Velocity Dispersion $\sigma$",
        "veldisp_gas": r"Gas Velocity Dispersion $\sigma_{\rm g}}$",
        "veldisp_star": r"Stellar Velocity Dispersion $\sigma_{*}$",
        "veldisp_bh": r"Black Hole Velocity Dispersion $\sigma_{\rm BH}$",
    }

    return key[combined_name]

