Velociraptor Python Library
===========================

[Velociraptor](http://github.com/pelahi/velociraptor-stf) catalogues provide
a signifciant amount of information, but applying units to it can be painful.
Here, the `unyt` python library is used to automatically apply units to
velociraptor data and perform generic halo-catalogue reduction. This library
is primarily intended to be used on [SWIFT](http://swiftsim.com) data that
has been post-processed with velociraptor, but can be used for any
velociraptor catalogue.

The internals of this library are based heavily on the internals of the
[`swiftsimio`](http://github.com/swiftsim/swiftsimio) library, and essentially
allow the velociraptor catalogue to be accessed in a lazy, object-oriented
way. This enables users to be able to reduce data quickly and in a
computationally efficient manner, without having to resort to using the
`h5py` library to manually load data (and hence manually apply units)!

Requirements
------------

The velociraptor library requires:

+ `unyt` and its dependencies
+ `h5py` and its dependencies

Note that for development, we suggest that you have `pytest` and `black`
installed. To create the plots in the example directory, you will need
the plotting framework `matplotlib`.

Why a custom library?
---------------------

This custom library, instead of something like `pandas`, allows us to
only load in the data that we require, and provide significant
context-dependent features that would not be available for something
generic. One example of this is the automatic labelling of properties,
as shown in the below example.

```python
from velociraptor import load
from velociraptor.tools import get_full_label

catalogue = load("/path/to/catalogue.properties")

stellar_masses = catalogue.apertures.mass_star_30_kpc
stellar_masses.convert_to_units("msun")

print(get_full_label(stellar_masses))
```
This outputs "Stellar Mass $M_*$ (30 kpc) $\left[M_\odot\right]$", which is
easy to add as, for example, a label on a plot.

Using the library
-----------------

The library has two main purposes: to enable easier exploration of the velociraptor
data, and to enable that data to be used with correct units.

We do this by providing sets of registration functions that turn the velociraptor
data into python data with units, associated with an object. Each of these
registration functions acts on different classes of properties. We describe
the available registration functions (these are not entirely complete!) below:

+ `metallicity`: properties that start with `Zmet`
+ `ids`: properties that are to do with IDs, such as Halo IDs or the most bound particle ID.
+ `energies`: properties starting with `E`
+ `rotational_support`: the `kappa` properties that describe rotational support
+ `star_formation_rate`: properties starting with `SFR`
+ `masses`: properties starting with `M` or `Mass`, e.g. `M_200crit`
+ `eigenvectors`: shape properties
+ `radii`: properties starting with `R`, that are various characteristic radii
+ `temperature`: properties starting with `T` such as the temperature of the halo
+ `veldisp`: velocity dispersion quantities
+ `structure_type`: the structure type properties
+ `velocities`: velocity properties
+ `positions`: various position properties, such as `Xc`
+ `concentration`: concentration of the halo, contains `cNFW`
+ `rvmax_quantities`: properties measured inside `RVmax`
+ `angular_momentum`: various angular momentum quantities starting with `L`
+ `projected_apertures`: several projected apertures and the quantities associated with them
+ `apertures`: properties measured within apertures
+ `fail_all`: a registration function that fails all tests, development only.

To extract properties, you need to instantiate a `VelociraptorCatalogue`. You
can do this by:
```python
from velociraptor import load

data = load("/path/to/catalogue.properties")

masses_200crit = data.masses.m_200crit
masses_200crit.convert_to_units("kg")
```
Here, we have the values of `M_200crit` stored in kgs, correctly applied based on
the unit metadata in the file.

If, for example, we wish to create a mass function of these values, we can use the tools,
```python
from velociraptor.tools import create_mass_function
from velociraptor.labels import get_full_label, get_mass_function_label
from unyt import Mpc

# Convert to stellar masses because that 'makes sense'
masses_200crit.convert_to_units("msun")

# Unfortunaetly, velociraptor doesn't curerntly store the boxsize in the catalogues:
box_volume = (25 * Mpc)**3

# Set the edges of our halo masses,
lowest_halo_mass = 1e9 * unyt.msun
highest_halo_mass = 1e14 * unyt.msun

bin_centers, mass_function, error = tools.create_mass_function(
    halo_masses, lowest_halo_mass, highest_halo_mass, box_volume
)
```
We now have a halo mass function, but the fun doesn't end there - we can get
pretty labels _automatically_ out of the python tools:
```
mass_label = get_full_label(masses_200crit)
mf_label = get_mass_function_label("200crit", mass_function)
```
If you want to try this out yourself, you can use the example scripts available in the
repository. Currently, we have scripts that create a HMF, SMF, and a galaxy-size
stellar-mass plot.


