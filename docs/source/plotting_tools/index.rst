Plotting Tools
==============

As well as the ability to extract data out of catalogues in a more efficient
way, the VELOCIraptor python toolkit also contains useful tools for creating
plots in a programatic way. These tools are available in the
:mod:`velociraptor.tools` module.

Labels
------

You can automatically generate labels for a given dataset using the
:func:`velociraptor.tools.labels.get_full_label` function, as follows:

.. code-block:: python

   from velociraptor import load
   from velociraptor.tools.labels import get_full_label

   data = load("...properties")
   m = data.masses.mass_200crit
   label = get_full_label(m)

This ``label`` is a LaTeX string containing a description of the dataset and
the symbolic units of whatever you converted it to.

You can also generate labels for mass functions:

.. code-block:: python

   from velociraptor.tools.labels import get_mass_function_label
   import unyt

   label = get_mass_function_label("*", unyt.Mpc**(-3))

which produces ``d$n(M_*)$/d$log_{10}M_*$ [Mpc$^{-3}$]``.


Lines
-----

One frequent activity is to generate binned lines for a figure, for instance
in a plot of x against y you may wish to have the mean or median of y in
equally spaced bins of x.

We provide two functions, :func:`velociraptor.tools.lines.binned_mean_line`
and :func:`velociraptor.tools.lines.binned_median_line`, to perform this task
for mean and median bins respectively. They both return scatter, with the
mean line returning the standard deviation and the median line by default
returning the 16-86 percentile scatter.

.. code-block:: python

   from velociraptor import load
   from velociraptor.tools.lines import binned_median_line
   from numpy import logspace
   from unyt import unyt_array, Solar_Mass

   data = load("...properties")

   bins = unyt_array(np.logspace(10, 15, 25), units=Solar_Mass)

   centers, median, deviation = binned_mean_line(
      x=data.apertures.mass_30_kpc.to(Solar_Mass),
      y=data.apertures.rhalfmass_30_kpc,
      x_bins=bins
   )


Mass Functions
--------------

Generating mass functions can be tricky, especially if you wish to plot them on
'true' axes (i.e. plotting mass on the x axis, not log(mass)). We provide
functionality to create the mass function through
:func:`velociraptor.tools.mass_functions.create_mass_function`. This returns the
bin centers, mass function, and poisson scatter in that bin. If you wish to use
your own mass bins, you can use the alternative
:func:`velociraptor.tools.mass_functions.create_mass_function_given_bins`.

.. code-block:: python

   from velociraptor import load
   from velociraptor.tools.mass_functions import create_mass_function
   from unyt import Solar_Mass

   data = load("...properties")
   masses = data.masses.mass_200mean
   box_volume = data.units.box_volume / (data.units.a**3)

   centers, mf, scatter = create_mass_function(
      masses=masses,
      lowest_mass=1e8*Solar_Mass,
      highest_mass=1e15*Solar_Mass,
      box_volume=box_volume,
      n_bins=25
   )
