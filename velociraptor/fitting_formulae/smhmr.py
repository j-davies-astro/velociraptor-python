"""
Fitting formulae for the stellar mass-halo mass relation.
"""

"""
Creates a stellar mass function plot for various velociraptor
catalogues.
"""

import unyt
import numpy as np

from velociraptor.catalogue.catalogue import VelociraptorCatalogue

from typing import Union, List


def moster(
    catalogue: VelociraptorCatalogue,
    mass_range: Union[unyt.unyt_array, List[unyt.unyt_quantity]] = [
        1e4 * unyt.msun,
        1e16 * unyt.msun,
    ],
    n_eval: int = 256,
):
    """
    The moster retaion (from Moster+ 2013). Original code provided by
    Matthieu Schaller. Takes:

    + catalogue, your velociraptor catalogue object
    + mass_range, a length 2 array with the lowest and highest halo mass
                  you would like the relation to be evaluated between
                  (default: 1e4 msun to 1e16 msun)
    + n_eval, the number of function evaluations (equally spaced in log (Mhalo))
              (default: 256)

    Returns:

    + halo_mass, the halo masses at which the relation is evaluated at
    + stellar_mass, the stellar masses matching with the above halo masses
    """

    z = catalogue.z
    halo_mass = (
        np.logspace(
            np.log10(mass_range[0].value), np.log10(mass_range[1].value), n_eval
        )
        * mass_range[0].units
    )

    stellar_mass = moster_raw(z, halo_mass.value) * halo_mass.units

    return halo_mass, stellar_mass


def moster_raw(z, Mhalo):
    """
    Stellar mass-halo mass relation from Moster+2013.

    Provided by Matthieu Schaller.
    """

    # Table 1
    M_10 = 11.590
    M_11 = 1.195
    N_10 = 0.0351
    N_11 = -0.0247
    beta_10 = 1.376
    beta_11 = -0.826
    gama_10 = 0.608
    gama_11 = 0.329

    # Equations 11 - 14
    log_M_1 = M_10 + M_11 * z / (z + 1)
    N = N_10 + N_11 * z / (z + 1)
    beta = beta_10 + beta_11 * z / (z + 1)
    gama = gama_10 + gama_11 * z / (z + 1)

    M_1 = 10 ** log_M_1

    # Equation 2
    Mstar_over_Mhalo = 2.0 * N * ((Mhalo / M_1) ** -beta + (Mhalo / M_1) ** gama) ** -1

    return Mstar_over_Mhalo * Mhalo


def behroozi(
    catalogue: VelociraptorCatalogue,
    mass_range: Union[unyt.unyt_array, List[unyt.unyt_quantity]] = [
        1e4 * unyt.msun,
        1e16 * unyt.msun,
    ],
    n_eval: int = 256,
):
    """
    The behroozi fit to the SMHMR (from Behroozi+ 2013). Original code provided by
    Matthieu Schaller. Takes:

    + catalogue, your velociraptor catalogue object
    + mass_range, a length 2 array with the lowest and highest halo mass
                  you would like the relation to be evaluated between
                  (default: 1e4 msun to 1e16 msun)
    + n_eval, the number of function evaluations (equally spaced in log (Mhalo))
              (default: 256)

    Returns:

    + halo_mass, the halo masses at which the relation is evaluated at
    + stellar_mass, the stellar masses matching with the above halo masses
    """

    z = catalogue.z
    halo_mass = (
        np.logspace(
            np.log10(mass_range[0].value), np.log10(mass_range[1].value), n_eval
        )
        * mass_range[0].units
    )

    stellar_mass = behroozi_raw(z, halo_mass.value) * halo_mass.units

    return halo_mass, stellar_mass


def behroozi_raw(z, Mhalo):
    """
    Stellar mass-halo mass relation from Behroozi +2013.

    Provided by Matthieu Schaller.
    """
    aexp = 1.0 / (1.0 + z)
    nu = np.exp(-4.0 * aexp ** 2)
    mh = Mhalo
    m1_0 = 11.514
    m1_a = -1.793
    m1_z = -0.251
    m1 = 10.0 ** (m1_0 + nu * (m1_a * (aexp - 1.0) + m1_z * z))
    eps0 = -1.777
    eps_a = -0.006
    eps_z = 0.000
    eps_a2 = -0.119
    eps = 10.0 ** (
        eps0 + nu * (eps_a * (aexp - 1.0) + eps_z * z) + eps_a2 * (aexp - 1.0)
    )
    alpha_0 = -1.412
    alpha_a = 0.731
    alpha = alpha_0 + nu * (alpha_a * (aexp - 1.0))
    delta_0 = 3.508
    delta_a = 2.608
    delta_z = -0.043
    delta = delta_0 + nu * (delta_a * (aexp - 1.0) + delta_z * z)
    gamma_0 = 0.316
    gamma_a = 1.319
    gamma_z = 0.279
    gamma = gamma_0 + nu * (gamma_a * (aexp - 1.0) + gamma_z * z)
    x = np.log10(mh / m1)
    f = -1.0 * np.log10(10.0 ** (alpha * x) + 1.0) + delta * (
        np.log10(1.0 + np.exp(x))
    ) ** gamma / (1.0 + np.exp(10.0 ** (-1.0 * x)))
    x0 = 0.0
    f0 = -1.0 * np.log10(10.0 ** (alpha * x0) + 1.0) + delta * (
        np.log10(1.0 + np.exp(x0))
    ) ** gamma / (1.0 + np.exp(10.0 ** (-1.0 * x0)))
    logmstar = np.log10(eps * m1) + f - f0
    return 10.0 ** logmstar

