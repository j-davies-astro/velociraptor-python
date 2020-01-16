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

    Parameters
    ----------

    filename: str
        Filename of the observational dataset that you wish to load.
        Should probably end in .hdf5. See the documentation for
        :class:`velociraptor.observations.objects.ObservationalData`
        for more information.

    Returns
    -------

    velociraptor.observations.objects.ObservationalData:
        Observational data instance read from file.
    """

    data = ObservationalData()
    data.load(filename)

    return data
