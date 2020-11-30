Creating Data Files
===================

There is functionality built into :mod:`velociraptor` to enable easy
creation of data files. To do this, you will need to fill an
:class:`velociraptor.observations.objects.ObservationalData` instance,
and then call the
:meth:`velociraptor.observations.objects.ObservationalData.write` method
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
   from astropy.cosmology import WMAP7 as cosmology
   import unyt
   import numpy as np
   import os

   input_filename = "Crain2009_GSMF.txt"
   delimiter = "\t"

   output_filename = "crain_2009.hdf5"
   output_directory = "gsmf"

   if not os.path.exists(output_directory):
      os.mkdir(output_directory)

   processed = ObservationalData()
   raw = np.loadtxt(input_filename, delimiter=delimiter)

   comment = f"Assuming Chabrier IMF. h-corrected for SWIFT using cosmology: {cosmology.name}."
   citation = "Crain et al. 2009 (GIMIC)"
   bibcode = "2009MNRAS.399.1773C"
   name = "GSMF from GIMIC"
   plot_as = "line"
   redshift = 0.0
   redshift_lower = 0.0
   redshift_upper = 0.2
   h = cosmology.h

   log_M = raw.T[0]
   M = 10 ** (log_M) * unyt.Solar_Mass / h
   Phi = (10**raw.T[1] * (h ** 3)) * unyt.Mpc ** (-3)

   processed.associate_x(M, scatter=None, comoving=True, description="Galaxy Stellar Mass")
   processed.associate_y(Phi, scatter=None, comoving=True, description="Phi (GSMF)")
   processed.associate_citation(citation, bibcode)
   processed.associate_name(name)
   processed.associate_comment(comment)
   processed.associate_redshift(redshift, redshift_lower, redshift_upper)
   processed.associate_plot_as(plot_as)
   processed.associate_cosmology(cosmology)

   output_path = f"{output_directory}/{output_filename}"

   if os.path.exists(output_path):
      os.remove(output_path)

   processed.write(filename=output_path)


Multi-Redshift Data
-------------------

Data from a single paper that has been collected at multiple redshifts (or a
single simulation, with multiple snapshots) should be stored in a
multi-redshift file. This will allow the most appropriate redshift from the
data to be plotted automatically when using the pipeline.

The :class:`velociraptor.observations.MultiRedshiftObservationalData` class
acts as a container for multiple instances of the
:class:`velociraptor.observations.ObservationalData` object, each for a
single redshift. However, the comments and cosmology are stored at 
the top level. Extending the example above to handle the multiple redshift
case:

.. code-block:: python

   from velociraptor.observations.objects import (
      ObservationalData,
      MultiRedshiftObservationalData,
   )
   from astropy.cosmology import WMAP7 as cosmology
   import unyt
   import numpy as np
   import os

   input_filenames = ["Crain2009_GSMF_z0.txt", "Crain2009_GSMF_z1.txt"]
   input_redshifts = [[0.0, 0.5], [0.5, 1.5]]
   delimiter = "\t"

   output_filename = "Crain_2009.hdf5"
   output_directory = "gsmf"
   comment = f"Assuming Chabrier IMF. h-corrected for SWIFT using cosmology: {cosmology.name}."
   citation = "Crain et al. 2009 (GIMIC)"
   bibcode = "2009MNRAS.399.1773C"
   name = "GSMF from GIMIC"

   if not os.path.exists(output_directory):
      os.mkdir(output_directory)

   multi_z = MultiRedshiftObservationalData()
   multi_z.associate_citation(citation, bibcode)
   multi_z.associate_name(name)
   multi_z.associate_comment(comment)
   multi_z.associate_cosmology(cosmology)
   multi_z.associate_maximum_number_of_returns(1)

   for filename, redshifts in zip(input_filenames, input_redshifts):
      processed = ObservationalData()
      raw = np.loadtxt(filename, delimiter=delimiter)

      plot_as = "line"
      redshift = 0.5 * sum(redshifts)
      redshift_lower, redshift_upper = redshifts
      h = cosmology.h

      log_M = raw.T[0]
      M = 10 ** (log_M) * unyt.Solar_Mass / h
      Phi = (10**raw.T[1] * (h ** 3)) * unyt.Mpc ** (-3)

      processed.associate_x(M, scatter=None, comoving=True, description="Galaxy Stellar Mass")
      processed.associate_y(Phi, scatter=None, comoving=True, description="Phi (GSMF)")
      processed.associate_redshift(redshift, redshift_lower, redshift_upper)
      processed.associate_plot_as(plot_as)

      multi_z.associate_dataset(processed)

   output_path = f"{output_directory}/{output_filename}"

   if os.path.exists(output_path):
      os.remove(output_path)

   multi_z.write(filename=output_path)


In this example, note that the following items are stored at the
top level:

+ Citation
+ Name
+ Comment
+ Cosmology

as the object is an abstraction for a single piece of academic work.
Below this, at the individual dataset level, we have

+ Actual data (e.g. x, y, associated with a single redshift)
+ Redshift (with bracketing)
+ Plotting commands (as some redshifts may have a very small number
  of objects, hence being better plotted as points, whereas some
  redshifts may require binning to a line).

Finally, we have the new ``associate_maximum_number_of_returns`` function.
This determines the maximum number of returned datasets from the
``load_datasets`` function. This is useful in cases where you have a large
number of individual datasets that cover very small ranges in redshift,
and you may only wish to plot one of them at a time on a given figure.
