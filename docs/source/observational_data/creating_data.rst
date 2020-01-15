Creating Data Files
===================

There is functionality built into :mod:`velociraptor` to enable easy
creation of data files. To do this, you will need to fill an
:class:`velociraptor.observations.objects.ObservationalData` instance,
and then call the
:mod:`velociraptor.observations.objects.ObservationalData.write` method
to save it out to file. There are several association functions that
you will need to call to register various metadata. An example converting
a TSV file to a :mod:`velociraptor`-compatible file is shown below.

General Rules
-------------

To ensure consistency between data files, follow the following suggestions:

+ Never use 'log' data on either axis; e.g. always include mass, not log(mass)
  even if the original paper used logarithmic quantities.
+ Always include all requested metadata (it doesn't take that long, but is very
  useful)!
+ Always remove all h-factors. Every file should be h-free.
+ Include a comment describing important aspects for the data, e.g. for a
  stellar mass function include the assumed IMF.
  
Example
-------

The input TSV file:

.. code-block:: bash

	#Crain et al 2009 (GIMIC)
	#Assuming Chabrier IMF and cosmology of
	# Omega_l = 0.75, Omega_0 = 0.045, h = 0.73
	#
	#GSMF weighted over all density regions
	#log(M) [Msun] Phi [(h^-1 Mpc)^-3]
	7.513259	-0.266989
	7.765294	-0.297700
	8.028524	-0.493567
	8.280272	-0.704415
	8.531949	-0.960297
	8.783625	-1.216179
	9.035397	-1.412015
	9.298460	-1.712962
	9.527172	-1.998804
	9.767462	-2.209621
	10.019115	-2.480514
	10.271149	-2.511225
	10.523422	-2.391822
	10.775695	-2.272418
	11.004742	-2.348101
	11.267685	-2.724105
	11.508166	-2.814830
	11.771062	-3.220858
	12.011042	-3.626822
	12.251666	-3.627479
	12.490953	-4.468774

Conversion file:

.. code-block:: python

	from velociraptor.observations.objects import ObservationalData
	import unyt
	import numpy as np
	import os

	input_filename = "path_to_csv_file.tsv"
	delimiter = "\t"
	raw = np.loadtxt(input_filename, delimiter=delimiter)

	output_filename = "crain_2009.hdf5"
	output_directory = "gsmf"

	if not os.path.exists(output_directory):
		os.mkdir(output_directory)

	# Create empty instance
	processed = ObservationalData()

	comment = "Assuming Chabrier IMF and cosmology of Omega_l = 0.75, Omega_0 = 0.045, h = 0.73. h-corrected for SWIFT."
	citation = "Crain et al. 2009 (GIMIC)"
	bibcode = "2009MNRAS.399.1773C"
	name = "GSMF from GIMIC"
	# Default - plot as a line for simulation data
	plot_as = "line"
	redshift = 0.0
	h = 0.73

	log_M = raw.T[0]
	M = 10 ** (log_M) * unyt.Solar_Mass / h
	Phi = (10**raw.T[1] * (h ** 3)) * unyt.Mpc ** (-3)

	processed.associate_x(M, scatter=None, comoving=True, description="Galaxy Stellar Mass")
	processed.associate_y(Phi, scatter=None, comoving=True, description="Phi (GSMF)")
	processed.associate_citation(citation, bibcode)
	processed.associate_name(name)
	processed.associate_comment(comment)
	processed.associate_redshift(redshift)
	processed.associate_plot_as(plot_as)

	output_path = f"{output_directory}/{output_filename}"

	if os.path.exists(output_path):
		os.remove(output_path)

	processed.write(filename=output_path)
