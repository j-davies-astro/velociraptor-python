"""
Sub-module for adding observational data to plots.

Includes the ObservationalData object and helper functions
to convert data to this new format.
"""

from velociraptor.observations.objects import ObservationalData


def load_observation(filename: str):
    """
    Load an observation from file filename. This should be in the
    standard velociraptor format.
    """

    data = ObservationalData()
    data.load(filename)

    return data
