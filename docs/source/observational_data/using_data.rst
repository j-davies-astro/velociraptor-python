Using "Observational Data" Files
================================

The observational data files created using :mod:`velociraptor` can be
opened into python objects through the use of the API available
in :mod:`velociraptor.observations`.

To load a file, you should use the :mod:`velociraptor.observations.load_observation`,
which will return an object of type
:class:`velociraptor.observations.objects.ObservationalData`.
This instance has several useful properties, and one key method,
:mod:`velociraptor.observations.objects.ObservationalData.plot_on_axes`.
This method allows you to provide a :class:`matplotlib.pyplot.Axes` object
to automatically plot the ``x`` and ``y`` fields on those axes.
Those arrays, ``x`` and ``y``, are instances of the
:class:`unyt.unyt_array` class, and as such you can use the ``convert_to_units``
method to convert these to whatever units you would like your axes to be in.
Unfortunately there is no integration within :mod:`matplotlib` to allow for
automatic conversion of data that is already plotted on a figure.

Example
-------

Below we create a plot of only the information out of a given ObservationalData
instance (and file) after loading it.

.. code-block:: python
	
	from velociraptor.observations import load_observation
	import matplotlib.pyplot as plt
	
	obs = load_observation("path/to/file.hdf5")
	
	fig, ax = plt.subplots()
	ax.loglog()
	
	obs.x.convert_to_units("kpc")
	obs.y.convert_to_units("msun")
	
	obs.plot_on_axes(ax)
	
	fig.savefig("out.png")
	
	