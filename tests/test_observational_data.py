"""
Tests the observational data loading / writing.
"""

from velociraptor.observations import (
    load_observations,
    ObservationalData,
    MultiRedshiftObservationalData,
)

import unyt
import os

from astropy.cosmology import FlatLambdaCDM

sample_cosmology = FlatLambdaCDM(H0=70, Om0=0.3, Ob0=0.048, name="test", m_nu=0.0)


def test_single_obs():
    """
    Tests that writing and reading a single observation works.
    """

    test_obs = ObservationalData()

    test_obs.associate_x(
        unyt.unyt_array([1, 2, 3], "Solar_Mass"),
        scatter=None,
        comoving=False,
        description="Galaxy Stellar Mass",
    )
    test_obs.associate_y(
        unyt.unyt_array([1, 2, 3], "kpc"),
        scatter=None,
        comoving=False,
        description="Galaxy Half-Mass Radius",
    )
    test_obs.associate_citation("Test et al. 2020", "Test001")
    test_obs.associate_name("Test Single Obs")
    test_obs.associate_comment("No Comment")
    test_obs.associate_redshift(0.1, redshift_lower=0.0, redshift_upper=0.2)
    test_obs.associate_plot_as("points")
    test_obs.associate_cosmology(sample_cosmology)

    if os.path.exists("test.hdf5"):
        os.remove("test.hdf5")
    test_obs.write("test.hdf5")

    comparison_obs = ObservationalData()
    comparison_obs.load("test.hdf5")

    assert comparison_obs.citation == test_obs.citation
    assert comparison_obs.bibcode == test_obs.bibcode
    assert comparison_obs.comment == test_obs.comment
    assert comparison_obs.redshift == test_obs.redshift
    assert comparison_obs.plot_as == test_obs.plot_as
    assert str(comparison_obs.cosmology) == str(test_obs.cosmology)
    assert (comparison_obs.x == test_obs.x).all()
    assert (comparison_obs.y == test_obs.y).all()

    os.remove("test.hdf5")


def test_multi_obs():
    """
    Tests that writing and reading a single observation works.
    """

    if os.path.exists("multi_z_test.hdf5"):
        os.remove("multi_z_test.hdf5")

    multi_z = MultiRedshiftObservationalData()
    multi_z.associate_citation("Test et al. 2020", "Test001")
    multi_z.associate_name("Test Single Obs")
    multi_z.associate_comment("No Comment")
    multi_z.associate_cosmology(sample_cosmology)

    for repeat, redshift in enumerate([0.5, 1.0, 1.5], start=1):
        # Repeat tests how we handle multiple lengths in the
        # data file.
        test_obs = ObservationalData()

        test_obs.associate_x(
            unyt.unyt_array([1, 2, 3] * repeat, "Solar_Mass"),
            scatter=None,
            comoving=False,
            description="Galaxy Stellar Mass",
        )
        test_obs.associate_y(
            unyt.unyt_array([1, 2, 3] * repeat, "kpc"),
            scatter=unyt.unyt_array([[1, 1], [1, 1], [1, 1]] * repeat, "kpc"),
            comoving=False,
            description="Galaxy Half-Mass Radius",
        )

        test_obs.associate_plot_as("points")
        test_obs.associate_redshift(
            redshift, redshift_lower=redshift - 0.25, redshift_upper=redshift + 0.25
        )

        multi_z.associate_dataset(test_obs)

    multi_z.write("multi_z_test.hdf5")

    # Now, can we read it?

    new_multi_z = MultiRedshiftObservationalData()
    new_multi_z.load("multi_z_test.hdf5")

    assert new_multi_z.citation == multi_z.citation
    assert new_multi_z.bibcode == multi_z.bibcode
    assert new_multi_z.comment == multi_z.comment
    assert new_multi_z.name == multi_z.name
    assert new_multi_z.code_version == multi_z.code_version

    for new, old in zip(new_multi_z.datasets, multi_z.datasets):
        assert new.citation == old.citation
        assert new.bibcode == old.bibcode
        assert new.comment == old.comment
        assert new.redshift == old.redshift
        assert new.plot_as == old.plot_as
        assert str(new.cosmology) == str(old.cosmology)
        assert (new.x == old.x).all()
        assert (new.y == old.y).all()

    # In the read version, test the overlaps.

    assert new_multi_z.get_datasets_overlapping_with([0.4, 0.6])[0].redshift == 0.5

    os.remove("multi_z_test.hdf5")
