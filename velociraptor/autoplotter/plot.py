"""
Functions that actually plot x against y.
"""

import matplotlib.pyplot as plt
import unyt

from velociraptor import VelociraptorCatalogue
from velociraptor.autoplotter.objects import VelociraptorLine
from typing import Tuple

import velociraptor.tools as tools


def scatter_x_against_y(
    x: unyt.unyt_array, y: unyt.unyt_quantity
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Creates a scatter of x against y (unyt arrays).
    """

    fig, ax = plt.subplots()

    ax.scatter(x.value, y.value, s=1, edgecolor="none", alpha=0.5)

    set_labels(ax=ax, x=x, y=y)

    return fig, ax


def decorate_axes(
    ax: plt.Axes, catalogue: VelociraptorCatalogue, loc: str = "bottom right"
) -> None:
    """
    Decorates the axes with information about the redshift and
    scale-factor.
    """

    # First need to parse the 'loc' string
    va, ha = loc.split(" ")

    if va == "bottom":
        y = 0.05
    elif va == "top":
        y = 0.95
    else:
        raise AttributeError(f"Unknown location string {loc}. Choose e.g. bottom right")

    if ha == "left":
        x = 0.05
    elif ha == "right":
        x = 0.95

    ax.text(
        x,
        y,
        f"$z={catalogue.z:2.3f}$\n$a={catalogue.a:2.3f}$",
        ha=ha,
        va=va,
        transform=ax.transAxes,
        multialignment=ha,
    )

    return


def set_labels(ax: plt.Axes, x: unyt.unyt_array, y: unyt.unyt_array) -> None:
    """
    Set the x and y labels for the axes.
    """

    ax.set_xlabel(tools.get_full_label(x))
    ax.set_ylabel(tools.get_full_label(y))

    return
