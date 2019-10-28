"""
Default registration functions.

If you add one, don't forget to add it to global_registration_functions
at the end of the file.
"""

import unyt

from typing import Union

from velociraptor.exceptions import RegistrationDoesNotMatchError
from velociraptor.units import VelociraptorUnits
from velociraptor.regex import cached_regex
from velociraptor.translator import (
    get_aperture_unit,
    get_particle_property_name_conversion,
)


def registration_fail_all(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Basic registration function showing function signature that is
    required and automatically fails all tests against itself.

    Function signature:

    + field_path: the name of the field
    + unit_system: a VelociraptorUnits instance that contains all unit
      information that is available from the velociraptor catalogue

    Return signature:
    
    + field_units: the units that correspond to field_path.
    + name: A fancy (possibly LaTeX'd) name for the field.
    + snake_case: A correct snake_case name for the field.
    """

    if field_path == "ThisFieldPathWouldNeverExist":
        return (
            unit_system.length,
            r"Fancy $N_{\rm ever}$ exists",
            "this_field_path_would_never_exist",
        )
    else:
        raise RegistrationDoesNotMatchError


def registration_apertures(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers aperture values by searching them with regex.
    """

    # Capture group 1: quantity
    # Capture group 2: particle type
    # Capture group 3: sf / nsf
    # Capture group 4: size of aperture

    match_string = "Aperture_([^_]*)_([a-zA-Z]*)?_?([a-zA-Z]*)?_?([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        quantity = match.group(1)
        ptype = match.group(2)
        star_forming = match.group(3)
        aperture_size = int(match.group(4))

        unit = get_aperture_unit(quantity, unit_system)
        name = get_particle_property_name_conversion(quantity, ptype)

        if star_forming:
            sf_in_name = f"{star_forming.upper()} "
        else:
            sf_in_name = ""

        full_name = f"{sf_in_name}{name} ({aperture_size} kpc)"
        snake_case = field_path.lower()

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_projected_apertures(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers aperture values by searching them with regex.
    """

    # Capture group 1: aperture number
    # Capture group 2: quantity
    # Capture group 3: particle type
    # Capture group 4: sf / nsf
    # Capture group 5: size of aperture

    match_string = (
        "Projected_aperture_([0-9])_([^_]*)_([a-zA-Z]*)?_?([a-zA-Z]*)?_?([0-9]*)_kpc"
    )
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        aperture = match.group(1)
        quantity = match.group(2)
        ptype = match.group(3)
        star_forming = match.group(4)
        aperture_size = int(match.group(5))

        unit = get_aperture_unit(quantity, unit_system)
        name = get_particle_property_name_conversion(quantity, ptype)

        if star_forming:
            sf_in_name = f"{star_forming.upper()} "
        else:
            sf_in_name = ""

        full_name = f"{sf_in_name}{name} (Projection {aperture}, {aperture_size} kpc)"
        snake_case = field_path.lower()

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_energies(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers all energy related quantities (those beginning with E).
    """

    if not field_path[0] == "E":
        raise RegistrationDoesNotMatchError

    if field_path[:5] == "Efrac":
        # This is an energy _fraction_
        full_name = "Energy Fraction"
        unit = unyt.dimensionless
    else:
        # This is an absolute energy
        if field_path[:4] == "Ekin":
            full_name = "Kinetic Energy"
        elif field_path[:4] == "Epot":
            full_name = "Potential Energy"
        else:
            full_name = "Energy"

        unit = unit_system.mass * unit_system.velocity * unit_system.velocity

    return unit, full_name, field_path.lower()


def registration_particle_ids(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers all quantities related to particle ids and halo ids (those beginning or ending with ID).
    """

    if not field_path[:2] == "ID" or field_path[:-2] == "ID":
        raise RegistrationDoesNotMatchError

    # As identifiers, all of these quantities are dimensionless
    unit = unyt.dimensionless

    if field_path == "ID":
        full_name = "Halo ID"
    elif field_path == "ID_mpb":
        full_name = "ID of Most Bound Particle"
    elif field_path == "ID_minpot":
        full_name = "ID of Particle at Potential Minimum"
    elif field_path == "hostHaloID":
        full_name = "Host Halo ID"
    else:
        full_name = "Generic ID"

    return unit, full_name, field_path.lower()


def registration_rotational_support(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers rotational support quantities (those beginning with K).
    Note that this corresponds to \kappa in Sales+2010 _not_ K.
    """

    if not field_path[0] == "K":
        raise RegistrationDoesNotMatchError

    # All quantities are ratios and so are dimensionless
    unit = unyt.dimensionless

    # Capture group 1: particle type
    # Capture group 2: star forming / not star forming

    match_string = "Krot_?([a-z]*)_?([a-z]*)?"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        ptype = match.group(1)
        star_forming = match.group(2)

        full_name = r"$\kappa_{{\rm rot}"

        if ptype:
            full_name += rf", {{\rm {ptype}}}"

        full_name += "}$"

        if star_forming:
            full_name += f" ({star_forming.upper()})"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_angular_momentum(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers values starting with L, those that represent
    angular momenta.
    """

    if not field_path[0] == "L":
        raise RegistrationDoesNotMatchError

    # All are angular momenta, so have same units.
    unit = unit_system.length * unit_system.velocity

    # Capture group 1: axis (x, y, z)
    # Capture group 2: radius within this was calculated, e.g. 200crit
    # Capture group 3: excluding or not excluding
    # Capture group 4: particle type
    # Capture group 5: star forming?

    match_string = "L([a-z])_?([A-Z]*[0-9]+[a-z]*)?_?(excl)?_?([a-z]*)_?([a-z]*)"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        axis = match.group(1)
        radius = match.group(2)
        excluding = match.group(3)
        ptype = match.group(4)
        star_forming = match.group(5)

        full_name = "$L_{"

        if axis:
            full_name += axis
        if radius:
            full_name += f", {{\rm {radius}}}"

        full_name += "}$"

        if ptype:
            full_name += " ("

            if excluding:
                full_name += "Excl. "

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registration for all mass-based quantities. (Start with M)
    """

    if not field_path[0] == "M":
        raise RegistrationDoesNotMatchError

    # All, obviously, have a unit of mass
    unit = unit_system.mass
    full_name = ""

    # Deal with special cases.
    if field_path == "Mvir":
        full_name = r"$M_{\rm vir}$"
    elif field_path == "Mass_FOF":
        full_name = r"$M_{\rm FOF}$"
    elif field_path == "Mass_tot":
        full_name = r"$M$"

    # General regex matching case.

    # Capture group 1: Mass or M
    # Capture group 2: radius within this was calculated, e.g. 200crit
    # Capture group 3: excluding?
    # Capture group 4: ptype
    # Capture group 5: star forming?
    # Capture group 6: "other"
    match_string = (
        "(Mass|M)_?([A-Z]*[0-9]+[a-z]*)?_?(excl)?_?([a-z]*)_?(nsf|sf)?_?([a-zA-Z0-9]*)"
    )
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match and not full_name:
        mass = match.group(1)
        radius = match.group(2)
        excluding = match.group(3)
        ptype = match.group(4)
        star_forming = match.group(5)
        other = match.group(6)

        full_name = "$M"

        if radius:
            full_name += f"_{{\rm {radius}}}"
        elif other:
            full_name += f"_{{\rm {other}}}"

        full_name += "$"

        if ptype:
            full_name += " ("

            if excluding:
                full_name += "Excl. "

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"

    return unit, full_name, field_path.lower()


def registration_rvmax_quantities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registration for all quantities measured within RVmax (Start with RVmax)
    """

    if not field_path[:5] == "RVmax":
        raise RegistrationDoesNotMatchError

    # Capture group 1: Eigenvector or velocity dispersion
    # Capture group 2: xx, xy, etc. for above
    # Capture group 3: Angular momentum quantity
    # Capture group 4: x, y, z for angular momentum
    # Capture group 5: catch all others
    match_string = "RVmax_((eig|veldisp)_([a-z]{2}))?_?(L([a-z]))?_?([a-zA-Z0-9_]*)"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        raise RegistrationDoesNotMatchError

    return  # TODO


def registration_radii(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registration for all radii quantities (start with R_)
    """

    # First, two special cases.
    if field_path == "Rvir":
        full_name = r"$R_{\rm vir}$"
    elif field_path == "Rmax":
        full_name = r"$R_{\rm max}$"
    elif field_path[:2] != "R_":
        raise RegistrationDoesNotMatchError

    unit = unit_system.length

    # Capture group 1: Characteristic scale
    # Capture group 2: Excluding?
    # Capture group 3: particle type
    # Capture group 4: star forming?
    match_string = "R_([a-zA-Z0-9]*)_?(excl)?_?([a-z]*)?_?(sf|nsf)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        radius = match.group(1)
        excluding = match.group(2)
        ptype = match.group(3)
        star_forming = match.group(4)

        full_name = "$R"

        if radius:
            full_name += f"_{{\rm {radius}}}"

        full_name += "$"

        if ptype:
            full_name += " ("

            if excluding:
                full_name += "Excl. "

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"

    return unit, full_name, field_path.lower()


# This must be placed at the bottom of the file so that we
# have defined all functions before getting to it.
global_registration_functions = [
    registration_particle_ids,
    registration_energies,
    registration_rotational_support,
    registration_masses,
    registration_radii,
    registration_rvmax_quantities,
    registration_angular_momentum,
    registration_projected_apertures,
    registration_apertures,
    registration_fail_all,
]

