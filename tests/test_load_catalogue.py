"""
Basic tests for loading a catalogue.
"""

from velociraptor import load


def test_basic_load_catalogue_no_crash(
    filename="/Users/mphf18/Desktop/halo_027_z00p101.properties"
):
    catalogue = load(filename)

    import pdb

    pdb.set_trace()

    return


if __name__ == "__main__":
    # Run all tests.

    test_basic_load_catalogue_no_crash()
