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
   box_volume = data.units.comoving_box_volume

   centers, mf, scatter = create_mass_function(
      masses=masses,
      lowest_mass=1e8*Solar_Mass,
      highest_mass=1e15*Solar_Mass,
      box_volume=box_volume,
      n_bins=25
   )

We also provide an adaptive mass function plotting code; this allows for
variable bin widths and is useful in the case where you have very few data
points. It is called through
:func:`velociraptor.tools.mass_functions.create_adaptive_mass_function` and
has the same parameters as ``create_mass_function`` except that ``n_bins`` is
now ``base_n_bins``. The algorithm works as follows:

1. Attempt to use the standard binning scheme based on fixed-width bins,
   by trawling the data from left (low :math:`M_*`) to right (high :math:`M_*`).
2. If you have passed more than :math:`n` items by the time you get to the next
   bin (standard is 0.2 dex in :math:`M_*`)$, create the bin as normal and plot
   the point as the median mass value.
3. If not, continue until you have at least :math:`n` items in the bin. Once you
   do, call this a new 'bin' with the right edge of the bin being the value
   you just found. Place the point at the median value of :math:`M_*` in this bin.
4. The highest mass value within a given bin becomes the right edge of that
   bin and hence the left edge of the next bin.
5. Once you have reached the end of the data, attempt to make one final
   bin with the leftovers. If there is only one item in the final bin, we extend
   the previous bin to include it.

By default :math:`n = 3`.