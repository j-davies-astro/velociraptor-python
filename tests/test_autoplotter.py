"""
Tests the autoplotter to see if all the expected fields are there.
"""

from velociraptor.autoplotter.objects import AutoPlotter
from unyt import unyt_quantity


def test_autoplotter():
    ap = AutoPlotter("tests/auto_plotter_test_file.yml")
    plot = ap.plots[0]

    assert plot.x == "masses.mass_200_crit"
    assert plot.x_log == False
    assert plot.x_label_override == "Halo Mass"

    assert plot.median_line.plot == True
    assert plot.median_line.start == unyt_quantity(1e10, units="Solar_Mass")

    return
