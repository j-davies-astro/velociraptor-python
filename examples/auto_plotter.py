"""
Example using the autoplotter library.

See auto_plotter_example.yml for the example
yaml file.
"""

from velociraptor.autoplotter.objects import AutoPlotter
from velociraptor.autoplotter.metadata import AutoPlotterMetadata
from velociraptor import load

catalogue = load("/Users/mphf18/Documents/science/halo_matching/ref/halo_2729.properties")

ap = AutoPlotter("auto_plotter_example.yml")

ap.link_catalogue(catalogue)
ap.create_plots("test_auto_plotter")

metadata = AutoPlotterMetadata(auto_plotter=ap)
metadata.write_metadata("test_auto_plotter/test_metadata.yml")

