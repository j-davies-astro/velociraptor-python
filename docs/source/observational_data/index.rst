Observational Data
==================

The functionality in this library is generally for dealing with data that
comes out of VELOCIraptor, and as such can only interface with a limited
number of simulation datasets. Frequently, it is useful to over-plot
data from, for example, other simulation groups, or even (_gasp_)
observational data. Here, "observational data" actually refers to
comparison data of any kind.

Dealing with this observational data is usually a mess of scattered
``.csv`` files. Here, we describe an interface that allows for structured
metadata to be created, and for easily usable files containing this
observational data to be saved to disk and recovered for future use.
The overarching abstraction here is a python object (of type
:class:`velociraptor.observations.objects.ObservationalData`) that can be
written to or read from file with HDF5 as the backing format.

This data can also be used with the :mod:`velociraptor.autoplotter`
functionality.

.. toctree::
    :maxdepth: 2

    file_format
    using_data
    creating_data

