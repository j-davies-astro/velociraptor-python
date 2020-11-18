Using "Observational Data" Files
================================

The observational data files created using :mod:`velociraptor` can be
opened into python objects through the use of the API available
in :mod:`velociraptor.observations`.

To load a file, you should use the
:func:`velociraptor.observations.load_observations`, which will return an
list of objects of type
:class:`velociraptor.observations.objects.ObservationalData`. Each instance
has several useful properties, and one key method,
:meth:`velociraptor.observations.objects.ObservationalData.plot_on_axes`.
This method allows you to provide a :class:`matplotlib.pyplot.Axes` object to
automatically plot the ``x`` and ``y`` fields on those axes. Those arrays,
``x`` and ``y``, are instances of the :class:`unyt.unyt_array` class, and as
such you can use the ``matplotlib_support`` environment within ``unyt`` to
automatically convert units to be consistent on the axes.

Example
-------

Below we create a plot of only the information out of a given ObservationalData
instance (and file) after loading it.

.. code-block:: python

   from velociraptor.observations import load_observations
   import matplotlib.pyplot as plt

   obs = load_observations("path/to/file.hdf5")[0]

   fig, ax = plt.subplots()
   ax.loglog()

   obs.x.convert_to_units("kpc")
   obs.y.convert_to_units("msun")

   obs.plot_on_axes(ax)

   fig.savefig("out.png")


You can provide multiple filenames, and possibly multi-redshift
datasets, along with a redshift bracket to only return datasets
that overlap with the given redshift range:

.. code-block:: python

   from velociraptor.observations import load_observation
   import matplotlib.pyplot as plt
   import unyt

   observations = load_observations(
      ["path/to/file_1.hdf5", "path/to/file_2.hdf5", "path/to/file_3.hdf5"],
      [0.0, 0.5] # Plot observations from z=0.0 to z=0.5
   )[0]

   fig, ax = plt.subplots()
   ax.loglog()

   with unyt.matplotlib_support:
      for obs in observations:
         obs.plot_on_axes(ax)

   fig.savefig("out.png")
