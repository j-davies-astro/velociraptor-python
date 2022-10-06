"""
Routines that provide translation of velociraptor quantities into something a
little more human readable, or to internal quantities.
"""

import unyt

from velociraptor.units import VelociraptorUnits


def VR_to_SOAP(particle_property_name: str):
    """
    Convert a VR property name into its SOAP counterpart (if one exists).
    """

    # dictionary with translations:
    #  VR_name: (SOAP_name, column index or -1 if 1D dataset)
    # (note: the first version of this dictionary was created by a script)
    VR_to_SOAP_translator = {
        "stellar_luminosities.u_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.u_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.u_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.u_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.g_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.g_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.g_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.g_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.r_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.r_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.r_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.r_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.i_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.i_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.i_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.i_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.z_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.z_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.z_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.z_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.Y_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.Y_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.Y_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.Y_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.J_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.J_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.J_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.J_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.H_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.H_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.H_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.H_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.K_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            8,
        ),
        "stellar_luminosities.K_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            8,
        ),
        "stellar_luminosities.K_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            8,
        ),
        "stellar_luminosities.K_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            8,
        ),
        "apertures.sfr_gas_100_kpc": ("exclusivesphere.100kpc.starformationrate", -1),
        "apertures.sfr_gas_10_kpc": ("exclusivesphere.10kpc.starformationrate", -1),
        "apertures.sfr_gas_30_kpc": ("exclusivesphere.30kpc.starformationrate", -1),
        "apertures.sfr_gas_50_kpc": ("exclusivesphere.50kpc.starformationrate", -1),
        "apertures.zmet_gas_100_kpc": ("exclusivesphere.100kpc.gasmassinmetals", -1),
        "apertures.zmet_gas_10_kpc": ("exclusivesphere.10kpc.gasmassinmetals", -1),
        "apertures.zmet_gas_30_kpc": ("exclusivesphere.30kpc.gasmassinmetals", -1),
        "apertures.zmet_gas_50_kpc": ("exclusivesphere.50kpc.gasmassinmetals", -1),
        "apertures.zmet_gas_sf_100_kpc": (
            "exclusivesphere.100kpc.starforminggasmassinmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_10_kpc": (
            "exclusivesphere.10kpc.starforminggasmassinmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_30_kpc": (
            "exclusivesphere.30kpc.starforminggasmassinmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_50_kpc": (
            "exclusivesphere.50kpc.starforminggasmassinmetals",
            -1,
        ),
        "apertures.zmet_star_100_kpc": (
            "exclusivesphere.100kpc.stellarmassinmetals",
            -1,
        ),
        "apertures.zmet_star_10_kpc": ("exclusivesphere.10kpc.stellarmassinmetals", -1),
        "apertures.zmet_star_30_kpc": ("exclusivesphere.30kpc.stellarmassinmetals", -1),
        "apertures.zmet_star_50_kpc": ("exclusivesphere.50kpc.stellarmassinmetals", -1),
        "apertures.mass_100_kpc": ("exclusivesphere.100kpc.totalmass", -1),
        "apertures.mass_10_kpc": ("exclusivesphere.10kpc.totalmass", -1),
        "apertures.mass_30_kpc": ("exclusivesphere.30kpc.totalmass", -1),
        "apertures.mass_50_kpc": ("exclusivesphere.50kpc.totalmass", -1),
        "apertures.mass_bh_100_kpc": (
            "exclusivesphere.100kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_bh_10_kpc": (
            "exclusivesphere.10kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_bh_30_kpc": (
            "exclusivesphere.30kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_bh_50_kpc": (
            "exclusivesphere.50kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_gas_100_kpc": ("exclusivesphere.100kpc.gasmass", -1),
        "apertures.mass_gas_10_kpc": ("exclusivesphere.10kpc.gasmass", -1),
        "apertures.mass_gas_30_kpc": ("exclusivesphere.30kpc.gasmass", -1),
        "apertures.mass_gas_50_kpc": ("exclusivesphere.50kpc.gasmass", -1),
        "apertures.mass_gas_sf_100_kpc": (
            "exclusivesphere.100kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_gas_sf_10_kpc": (
            "exclusivesphere.10kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_gas_sf_30_kpc": (
            "exclusivesphere.30kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_gas_sf_50_kpc": (
            "exclusivesphere.50kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_hight_100_kpc": ("exclusivesphere.100kpc.totalmass", -1),
        "apertures.mass_hight_10_kpc": ("exclusivesphere.10kpc.totalmass", -1),
        "apertures.mass_hight_30_kpc": ("exclusivesphere.30kpc.totalmass", -1),
        "apertures.mass_hight_50_kpc": ("exclusivesphere.50kpc.totalmass", -1),
        "apertures.mass_star_100_kpc": ("exclusivesphere.100kpc.stellarmass", -1),
        "apertures.mass_star_10_kpc": ("exclusivesphere.10kpc.stellarmass", -1),
        "apertures.mass_star_30_kpc": ("exclusivesphere.30kpc.stellarmass", -1),
        "apertures.mass_star_50_kpc": ("exclusivesphere.50kpc.stellarmass", -1),
        "apertures.npart_bh_100_kpc": (
            "exclusivesphere.100kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_bh_10_kpc": (
            "exclusivesphere.10kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_bh_30_kpc": (
            "exclusivesphere.30kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_bh_50_kpc": (
            "exclusivesphere.50kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_gas_100_kpc": (
            "exclusivesphere.100kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_gas_10_kpc": (
            "exclusivesphere.10kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_gas_30_kpc": (
            "exclusivesphere.30kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_gas_50_kpc": (
            "exclusivesphere.50kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_star_100_kpc": (
            "exclusivesphere.100kpc.numberofstarparticles",
            -1,
        ),
        "apertures.npart_star_10_kpc": (
            "exclusivesphere.10kpc.numberofstarparticles",
            -1,
        ),
        "apertures.npart_star_30_kpc": (
            "exclusivesphere.30kpc.numberofstarparticles",
            -1,
        ),
        "apertures.npart_star_50_kpc": (
            "exclusivesphere.50kpc.numberofstarparticles",
            -1,
        ),
        "apertures.rhalfmass_gas_100_kpc": (
            "exclusivesphere.100kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_gas_10_kpc": (
            "exclusivesphere.10kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_gas_30_kpc": (
            "exclusivesphere.30kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_gas_50_kpc": (
            "exclusivesphere.50kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_star_100_kpc": (
            "exclusivesphere.100kpc.halfmassradiusstars",
            -1,
        ),
        "apertures.rhalfmass_star_10_kpc": (
            "exclusivesphere.10kpc.halfmassradiusstars",
            -1,
        ),
        "apertures.rhalfmass_star_30_kpc": (
            "exclusivesphere.30kpc.halfmassradiusstars",
            -1,
        ),
        "apertures.rhalfmass_star_50_kpc": (
            "exclusivesphere.50kpc.halfmassradiusstars",
            -1,
        ),
        "angular_momentum.lx_200c_gas": ("so.200_crit.angularmomentumgas", 0),
        "angular_momentum.lx_200c_star": ("so.200_crit.angularmomentumstars", 0),
        "angular_momentum.lx_200m_gas": ("so.200_mean.angularmomentumgas", 0),
        "angular_momentum.lx_200m_star": ("so.200_mean.angularmomentumstars", 0),
        "angular_momentum.lx_bn98_gas": ("so.bn98.angularmomentumgas", 0),
        "angular_momentum.lx_bn98_star": ("so.bn98.angularmomentumstars", 0),
        "angular_momentum.lx_gas": ("boundsubhaloproperties.angularmomentumgas", 0),
        "angular_momentum.lx_star": ("boundsubhaloproperties.angularmomentumstars", 0),
        "angular_momentum.ly_200c_gas": ("so.200_crit.angularmomentumgas", 1),
        "angular_momentum.ly_200c_star": ("so.200_crit.angularmomentumstars", 1),
        "angular_momentum.ly_200m_gas": ("so.200_mean.angularmomentumgas", 1),
        "angular_momentum.ly_200m_star": ("so.200_mean.angularmomentumstars", 1),
        "angular_momentum.ly_bn98_gas": ("so.bn98.angularmomentumgas", 1),
        "angular_momentum.ly_bn98_star": ("so.bn98.angularmomentumstars", 1),
        "angular_momentum.ly_gas": ("boundsubhaloproperties.angularmomentumgas", 1),
        "angular_momentum.ly_star": ("boundsubhaloproperties.angularmomentumstars", 1),
        "angular_momentum.lz_200c_gas": ("so.200_crit.angularmomentumgas", 2),
        "angular_momentum.lz_200c_star": ("so.200_crit.angularmomentumstars", 2),
        "angular_momentum.lz_200m_gas": ("so.200_mean.angularmomentumgas", 2),
        "angular_momentum.lz_200m_star": ("so.200_mean.angularmomentumstars", 2),
        "angular_momentum.lz_bn98_gas": ("so.bn98.angularmomentumgas", 2),
        "angular_momentum.lz_bn98_star": ("so.bn98.angularmomentumstars", 2),
        "angular_momentum.lz_gas": ("boundsubhaloproperties.angularmomentumgas", 2),
        "angular_momentum.lz_star": ("boundsubhaloproperties.angularmomentumstars", 2),
        "masses.mass_200crit": ("so.200_crit.totalmass", -1),
        "masses.mass_200crit_gas": ("so.200_crit.gasmass", -1),
        "masses.mass_200crit_star": ("so.200_crit.stellarmass", -1),
        "masses.mass_200mean": ("so.200_mean.totalmass", -1),
        "masses.mass_200mean_gas": ("so.200_mean.gasmass", -1),
        "masses.mass_200mean_star": ("so.200_mean.stellarmass", -1),
        "masses.mass_bn98": ("so.bn98.totalmass", -1),
        "masses.mass_bn98_gas": ("so.bn98.gasmass", -1),
        "masses.mass_bn98_star": ("so.bn98.stellarmass", -1),
        "masses.mass_fof": ("fofsubhaloproperties.totalmass", -1),
        "masses.mass_bh": ("boundsubhaloproperties.blackholesdynamicalmass", -1),
        "masses.mass_gas": ("boundsubhaloproperties.gasmass", -1),
        "masses.mass_star": ("boundsubhaloproperties.stellarmass", -1),
        "masses.mass_tot": ("boundsubhaloproperties.totalmass", -1),
        "projected_apertures.projected_1_sfr_gas_100_kpc": (
            "projectedaperture.100kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_sfr_gas_10_kpc": (
            "projectedaperture.10kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_sfr_gas_30_kpc": (
            "projectedaperture.30kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_sfr_gas_50_kpc": (
            "projectedaperture.50kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_mass_100_kpc": (
            "projectedaperture.100kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_10_kpc": (
            "projectedaperture.10kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_30_kpc": (
            "projectedaperture.30kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_50_kpc": (
            "projectedaperture.50kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_100_kpc": (
            "projectedaperture.100kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_10_kpc": (
            "projectedaperture.10kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_30_kpc": (
            "projectedaperture.30kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_50_kpc": (
            "projectedaperture.50kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_100_kpc": (
            "projectedaperture.100kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_10_kpc": (
            "projectedaperture.10kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_30_kpc": (
            "projectedaperture.30kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_50_kpc": (
            "projectedaperture.50kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_100_kpc": (
            "projectedaperture.100kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_10_kpc": (
            "projectedaperture.10kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_30_kpc": (
            "projectedaperture.30kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_50_kpc": (
            "projectedaperture.50kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_100_kpc": (
            "projectedaperture.100kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_10_kpc": (
            "projectedaperture.10kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_30_kpc": (
            "projectedaperture.30kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_50_kpc": (
            "projectedaperture.50kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_100_kpc": (
            "projectedaperture.100kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_10_kpc": (
            "projectedaperture.10kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_30_kpc": (
            "projectedaperture.30kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_50_kpc": (
            "projectedaperture.50kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_mass_100_kpc": (
            "projectedaperture.100kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_10_kpc": (
            "projectedaperture.10kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_30_kpc": (
            "projectedaperture.30kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_50_kpc": (
            "projectedaperture.50kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_100_kpc": (
            "projectedaperture.100kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_10_kpc": (
            "projectedaperture.10kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_30_kpc": (
            "projectedaperture.30kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_50_kpc": (
            "projectedaperture.50kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_100_kpc": (
            "projectedaperture.100kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_10_kpc": (
            "projectedaperture.10kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_30_kpc": (
            "projectedaperture.30kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_50_kpc": (
            "projectedaperture.50kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_100_kpc": (
            "projectedaperture.100kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_10_kpc": (
            "projectedaperture.10kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_30_kpc": (
            "projectedaperture.30kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_50_kpc": (
            "projectedaperture.50kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_100_kpc": (
            "projectedaperture.100kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_10_kpc": (
            "projectedaperture.10kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_30_kpc": (
            "projectedaperture.30kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_50_kpc": (
            "projectedaperture.50kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_100_kpc": (
            "projectedaperture.100kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_10_kpc": (
            "projectedaperture.10kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_30_kpc": (
            "projectedaperture.30kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_50_kpc": (
            "projectedaperture.50kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_mass_100_kpc": (
            "projectedaperture.100kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_10_kpc": (
            "projectedaperture.10kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_30_kpc": (
            "projectedaperture.30kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_50_kpc": (
            "projectedaperture.50kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_100_kpc": (
            "projectedaperture.100kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_10_kpc": (
            "projectedaperture.10kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_30_kpc": (
            "projectedaperture.30kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_50_kpc": (
            "projectedaperture.50kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_100_kpc": (
            "projectedaperture.100kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_10_kpc": (
            "projectedaperture.10kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_30_kpc": (
            "projectedaperture.30kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_50_kpc": (
            "projectedaperture.50kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_100_kpc": (
            "projectedaperture.100kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_10_kpc": (
            "projectedaperture.10kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_30_kpc": (
            "projectedaperture.30kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_50_kpc": (
            "projectedaperture.50kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_100_kpc": (
            "projectedaperture.100kpc.projz.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_10_kpc": (
            "projectedaperture.10kpc.projz.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_30_kpc": (
            "projectedaperture.30kpc.projz.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_50_kpc": (
            "projectedaperture.50kpc.projz.halfmassradiusstars",
            -1,
        ),
        "radii.r_200crit": ("so.200_crit.soradius", -1),
        "radii.r_200mean": ("so.200_mean.soradius", -1),
        "radii.r_bn98": ("so.bn98.soradius", -1),
        "radii.r_halfmass": ("boundsubhaloproperties.halfmassradiustotal", -1),
        "radii.r_halfmass_gas": ("boundsubhaloproperties.halfmassradiusgas", -1),
        "radii.r_halfmass_star": ("boundsubhaloproperties.halfmassradiusstars", -1),
        "star_formation_rate.sfr_gas": ("boundsubhaloproperties.starformationrate", -1),
        "spherical_overdensities.lx_gas_1000_rhocrit": (
            "so.1000_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_100_rhocrit": (
            "so.100_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_200_rhocrit": (
            "so.200_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_2500_rhocrit": (
            "so.2500_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_500_rhocrit": (
            "so.500_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_star_1000_rhocrit": (
            "so.1000_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_100_rhocrit": (
            "so.100_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_200_rhocrit": (
            "so.200_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_2500_rhocrit": (
            "so.2500_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_500_rhocrit": (
            "so.500_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.ly_gas_1000_rhocrit": (
            "so.1000_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_100_rhocrit": (
            "so.100_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_200_rhocrit": (
            "so.200_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_2500_rhocrit": (
            "so.2500_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_500_rhocrit": (
            "so.500_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_star_1000_rhocrit": (
            "so.1000_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_100_rhocrit": (
            "so.100_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_200_rhocrit": (
            "so.200_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_2500_rhocrit": (
            "so.2500_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_500_rhocrit": (
            "so.500_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.lz_gas_1000_rhocrit": (
            "so.1000_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_100_rhocrit": (
            "so.100_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_200_rhocrit": (
            "so.200_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_2500_rhocrit": (
            "so.2500_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_500_rhocrit": (
            "so.500_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_star_1000_rhocrit": (
            "so.1000_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_100_rhocrit": (
            "so.100_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_200_rhocrit": (
            "so.200_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_2500_rhocrit": (
            "so.2500_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_500_rhocrit": (
            "so.500_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.mass_1000_rhocrit": ("so.1000_crit.totalmass", -1),
        "spherical_overdensities.mass_100_rhocrit": ("so.100_crit.totalmass", -1),
        "spherical_overdensities.mass_200_rhocrit": ("so.200_crit.totalmass", -1),
        "spherical_overdensities.mass_2500_rhocrit": ("so.2500_crit.totalmass", -1),
        "spherical_overdensities.mass_500_rhocrit": ("so.500_crit.totalmass", -1),
        "spherical_overdensities.mass_gas_1000_rhocrit": ("so.1000_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_100_rhocrit": ("so.100_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_200_rhocrit": ("so.200_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_2500_rhocrit": ("so.2500_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_500_rhocrit": ("so.500_crit.gasmass", -1),
        "spherical_overdensities.mass_star_1000_rhocrit": (
            "so.1000_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_100_rhocrit": (
            "so.100_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_200_rhocrit": (
            "so.200_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_2500_rhocrit": (
            "so.2500_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_500_rhocrit": (
            "so.500_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.r_1000_rhocrit": ("so.1000_crit.soradius", -1),
        "spherical_overdensities.r_100_rhocrit": ("so.100_crit.soradius", -1),
        "spherical_overdensities.r_200_rhocrit": ("so.200_crit.soradius", -1),
        "spherical_overdensities.r_2500_rhocrit": ("so.2500_crit.soradius", -1),
        "spherical_overdensities.r_500_rhocrit": ("so.500_crit.soradius", -1),
        "structure_type.structuretype": ("vr.structuretype", -1),
        "black_hole_masses.max": (
            "boundsubhaloproperties.mostmassiveblackholemass",
            -1,
        ),
        "temperature.t_gas": ("boundsubhaloproperties.gastemperature", -1),
        "temperature.t_gas_hight_incl": (
            "boundsubhaloproperties.gastemperaturewithoutcoolgas",
            -1,
        ),
        "velocities.vxc": ("boundsubhaloproperties.centreofmassvelocity", 0),
        "velocities.vyc": ("boundsubhaloproperties.centreofmassvelocity", 1),
        "velocities.vzc": ("boundsubhaloproperties.centreofmassvelocity", 2),
        "velocities.vmax": ("boundsubhaloproperties.maximumcircularvelocity", -1),
        "positions.xc": ("boundsubhaloproperties.centreofmass", 0),
        "positions.xcmbp": ("vr.centreofpotential", 0),
        "positions.xcminpot": ("vr.centreofpotential", 0),
        "positions.yc": ("boundsubhaloproperties.centreofmass", 1),
        "positions.ycmbp": ("vr.centreofpotential", 1),
        "positions.ycminpot": ("vr.centreofpotential", 1),
        "positions.zc": ("boundsubhaloproperties.centreofmass", 2),
        "positions.zcmbp": ("vr.centreofpotential", 2),
        "positions.zcminpot": ("vr.centreofpotential", 2),
        "metallicity.zmet_gas": ("boundsubhaloproperties.gasmassinmetals", -1),
        "metallicity.zmet_star": ("boundsubhaloproperties.stellarmassinmetals", -1),
        "ids.hosthaloid": ("vr.hosthaloid", -1),
        "number.bh": ("boundsubhaloproperties.numberofblackholeparticles", -1),
        "number.gas": ("boundsubhaloproperties.numberofgasparticles", -1),
        "number.star": ("boundsubhaloproperties.numberofstarparticles", -1),
        "veldisp.veldisp_xx_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            0,
        ),
        "veldisp.veldisp_xx_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            0,
        ),
        "veldisp.veldisp_xy_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            3,
        ),
        "veldisp.veldisp_xy_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            3,
        ),
        "veldisp.veldisp_xz_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            4,
        ),
        "veldisp.veldisp_xz_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            4,
        ),
        "veldisp.veldisp_yx_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            3,
        ),
        "veldisp.veldisp_yx_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            3,
        ),
        "veldisp.veldisp_yy_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            1,
        ),
        "veldisp.veldisp_yy_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            1,
        ),
        "veldisp.veldisp_yz_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            5,
        ),
        "veldisp.veldisp_yz_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            5,
        ),
        "veldisp.veldisp_zx_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            4,
        ),
        "veldisp.veldisp_zx_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            4,
        ),
        "veldisp.veldisp_zy_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            5,
        ),
        "veldisp.veldisp_zy_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            5,
        ),
        "veldisp.veldisp_zz_gas": (
            "boundsubhaloproperties.gasvelocitydispersionmatrix",
            2,
        ),
        "veldisp.veldisp_zz_star": (
            "boundsubhaloproperties.stellarvelocitydispersionmatrix",
            2,
        ),
    }

    try:
        return VR_to_SOAP_translator[particle_property_name]
    except KeyError:
        raise NotImplementedError(
            f"No SOAP analogue for property {particle_property_name}!"
        )


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
    corrected_name = typo_correct(unit_name).lower()

    key = {
        "sfr": unit_system.star_formation_rate,
        "zmet": unit_system.metallicity,
        "mass": unit_system.mass,
        "npart": unyt.dimensionless,
        "rhalfmass": unit_system.length,
        "veldisp": unit_system.velocity,
        "r": unit_system.length,
        "lx": unit_system.length * unit_system.velocity,
        "ly": unit_system.length * unit_system.velocity,
        "lz": unit_system.length * unit_system.velocity,
    }

    return key.get(corrected_name, None)


def get_particle_property_name_conversion(name: str, ptype: str):
    """
    Takes an internal velociraptor particle property and returns
    a fancier name for use in plot legends. Typically used for the
    complex aperture properties.
    """

    corrected_name = typo_correct(name)

    combined_name = f"{corrected_name}_{ptype}".lower()

    key = {
        "sfr_": "SFR $\dot{\\rho}_*$",
        "sfr_gas": "Gas SFR $\dot{\\rho}_*$",
        "zmet_": "Metallicity $Z$",
        "zmet_gas": "Gas Metallicity $Z_{\\rm g}$",
        "zmet_star": "Star Metallicity $Z_*$",
        "zmet_bh": "Black Hole Metallicity $Z_{\\rm BH}$",
        "mass_": "Mass $M$",
        "mass_gas": "Gas Mass $M_{\\rm g}$",
        "mass_star": "Stellar Mass $M_*$",
        "mass_bh": "Black Hole Mass $M_{\\rm BH}$",
        "mass_interloper": "Mass of Interlopers",
        "npart_": "Number of Particles $N$",
        "npart_gas": "Number of Gas Particles $N_{\\rm g}$",
        "npart_star": "Number of Stellar Particles $N_*$",
        "npart_bh": "Black Hole Mass $N_{\\rm BH}$",
        "npart_interloper": "Number of Interlopers",
        "rhalfmass_": "Half-mass Radius $R_{50}$",
        "rhalfmass_gas": "Gas Half-mass Radius $R_{50, {\\rm g}}$",
        "rhalfmass_star": "Stellar Half-mass Radius $R_{50, *}$",
        "rhalfmass_bh": "Black Hole Half-mass Radius $R_{50, {\\rm BH}}$",
        "r_": "Radius $R_{\\rm SO}$",
        "veldisp_": "Velocity Dispersion $\sigma$",
        "veldisp_gas": "Gas Velocity Dispersion $\sigma_{\\rm g}}$",
        "veldisp_star": "Stellar Velocity Dispersion $\sigma_{*}$",
        "veldisp_bh": "Black Hole Velocity Dispersion $\sigma_{\\rm BH}$",
        "subgridmasses_aperture_total_solar_mass_bh": "Subgrid Black Hole Mass $M_{\\rm BH}$",
    }

    return key.get(combined_name, corrected_name)
