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
+ `python3.6` or above

Note that for development, we suggest that you have `pytest` and `black`
installed. To create the plots in the example directory, you will need
the plotting framework `matplotlib`.

Installation
------------

For now, you can install the library by downloading this repository, changing
to the top-level directory and running:
```
pip3 install .
```

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
```python
mass_label = get_full_label(masses_200crit)
mf_label = get_mass_function_label("200crit", mass_function)
```
If you want to try this out yourself, you can use the example scripts available in the
repository. Currently, we have scripts that create a HMF, SMF, and a galaxy-size
stellar-mass plot.


Particles Files
---------------

With the `velociraptor` tool, you can easily extract the groups information available
from the catalogues by using the tools found in `velociraptor.particles`. To do this,
you must first open the groups file, and then you may extract the particles belonging
to individual haloes in the following way:
```python
from velociraptor.particles import load_groups
from velociraptor import load

catalogue = load("/path/to.properties")
# Passing the catalogue file is not required but is is necessary to make use
# of all features
groups = load_groups("/path/to.catalog_groups", catalogue=catalogue)

# This returns two instances of the VelociraptorParticles class.
# The first contains all bound particles, and the second contains all unbound particles.
particles, unbound_particles = groups.extract_halo(halo_id=123)

# To view the contents of the particles files, you can use:
bound_particle_ids = particles.particle_ids
unbound_bound_particle_ids = unbound_particles.particle_ids

halo_mass = particles.mass_200crit
```
See below for a more advanced use of this, to extract a `swiftsimio` dataset corresponding
to the particles that are available in this group.

SWIFTsimIO Integration
----------------------

Using the `VelociraptorParticles` class, it is possible to find which particles
belong to a given halo. We also provide functionality to quickly (by using spatial
metadata in the snapshots) extract the regions around haloes, and the specific particles
in each halo itself. To do this, you will need to use the tools in `velociraptor.swift`,
in particular the `to_swiftsimio_dataset` function. It is used as follows:
```python
data, mask = to_swiftsimio_dataset(particles, "/path/to/snapshot.hdf5", generate_extra_mask=True)

# The dataset that is returned is only spatially masked. It only contains particles that
# are within the same top-level cell as the region that the halo overlaps with, but it can
# be accessed as if it is just a regular `swiftsimio` dataset. For instance
gas_densities = data.gas.densities
redshift = data.metadata.z
hydro_info = data.metadata.hydro_info

# The extra mask allows for you to find only the particles that are classed as being
# part of the FoF group (in this case only the bound particles). To select the gas densities
# of particles in the group, for example, perform the following:
gas_densities_only_fof = data.gas.densities[mask.gas]
# Or the dark matter co-ordinates
dm_coordinates_only_fof = data.dark_matter.coordinates[mask.dark_matter]

# All of the swiftsimio features are available, so for instance you can generate
# a py-sphviewer instance out of these
from swiftismio.visualisation.sphviewer import SPHViewerWrapper
sphviewer = SPHViewerWrapper(data.gas)
sphviewer.quickview(xsize=1024,ysize=1024,r="infinity")
...
```
To see these functions in action, you can check out the examples available in
`examples/swift_integration*.py` in this repository.




