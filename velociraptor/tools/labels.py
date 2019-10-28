"""
Tools for generating labels from catalogue datasets.
"""

import unyt


def get_full_label(dataset: unyt.unyt_array):
    """
    Get the full label for one of our VelociraptorCatalogue datasets.
    This will get the automatically generated name and concatenate
    it with the _current_ untis for that dataset.
    """

    unit_tex = dataset.units.latex_representation()

    full_label = f"{dataset.name} [${unit_tex}$]"

    return full_label
