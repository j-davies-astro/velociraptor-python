"""
Example using the autoplotter library.

See auto_plotter_example.yml for the example
yaml file.
"""

from velociraptor.autoplotter.objects import AutoPlotter
from velociraptor import load

catalogue = load("/Users/mphf18/Desktop/halo_027_z00p101.properties")

ap = AutoPlotter("auto_plotter_example.yml")

ap.link_catalogue(catalogue)
ap.create_plots("test_auto_plotter")
