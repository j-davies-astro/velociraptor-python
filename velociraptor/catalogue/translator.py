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
        "SFR_": "SFR $\dot{\\rho}_*$",
        "SFR_gas": "Gas SFR $\dot{\\rho}_*$",
        "Zmet_": "Metallicity $Z$",
        "Zmet_gas": "Gas Metallicity $Z_{\\rm g}$",
        "Zmet_star": "Star Metallicity $Z_*$",
        "Zmet_bh": "Black Hole Metallicity $Z_{\\rm BH}$",
        "mass_": "Mass $M$",
        "mass_gas": "Gas Mass $M_{\\rm g}$",
        "mass_star": "Stellar Mass $M_*$",
        "mass_bh": "Black Hole Mass $M_{\\rm BH}$",
        "npart_": "Number of Particles $N$",
        "npart_gas": "Number of Gas Particles $N_{\\rm g}$",
        "npart_star": "Number of Stellar Particles $N_*$",
        "npart_bh": "Black Hole Mass $N_{\\rm BH}$",
        "rhalfmass_": "Half-mass Radius $R_{50}$",
        "rhalfmass_gas": "Gas Half-mass Radius $R_{50, {\\rm g}}$",
        "rhalfmass_star": "Stellar Half-mass Radius $R_{50, *}$",
        "rhalfmass_bh": "Black Hole Half-mass Radius $R_{50, {\\rm BH}}$",
        "veldisp_": "Velocity Dispersion $\sigma$",
        "veldisp_gas": "Gas Velocity Dispersion $\sigma_{\\rm g}}$",
        "veldisp_star": "Stellar Velocity Dispersion $\sigma_{*}$",
        "veldisp_bh": "Black Hole Velocity Dispersion $\sigma_{\\rm BH}$",
        "SubgridMasses_aperture_total_solar_mass_bh": "Subgrid Black Hole Mass $M_{\\rm BH}$",
    }

    return key[combined_name]
