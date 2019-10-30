"""
SWIFTsimIO integration.

This allows users to load the contents of various haloes as `swiftsimio`
datasets in a computationally efficient way.
"""


import swiftsimio
import numpy as np

from velociraptor.particles.particles import VelociraptorParticles


from collections import namedtuple


def to_swiftsimio_dataset(
    particles: VelociraptorParticles,
    snapshot_filename,
    generate_extra_mask: bool = False,
) -> swiftsimio.reader.SWIFTDataset:
    """
    Loads a VelociraptorParticles instance for one halo into a 
    `swiftsimio` masked dataset.

    Initially, this uses `r_max` to perform a spatial mask, and
    then returns the `swiftsimio` dataset and a secondary mask
    that may be used to extract only the particles that are
    part of the FoF group.

    You will need to instantiate the VelociraptorParticles instance
    with an associated catalogue to use this feature, as it requires
    the knowledge of `r_max`.
    
    Takes three arguments:

    + particles, the VelociraptorParticles instance,
    + snapshot_filename, the path to the associated SWIFT snapshot.
    + generate_extra_mask, whether or not to generate the secondary 
                           mask object that allows for the extraction
                           of particles that are present only in the
                           FoF group.

    It returns:

    + data, the swiftsimio dataset
    + mask, an object containing for all available datasets in the
            swift dataset. The initial masking is performed on a
            spatial only basis, and this is required to only extract
            the particles in the FoF group as identified by 
            velociraptor. This is only provided if generate_extra_mask
            has a truthy value.
    """

    # First use the swiftsimio spatial masking to constrain our dataset
    # to only contain particles within the cube that contains the halo
    # (this is only approximate down to the swift cell size)
    swift_mask = swiftsimio.mask(snapshot_filename, spatial_only=True)

    spatial_mask = [
        [paritcles.x - particles.rmax, particles.x + particles.rmax],
        [paritcles.y - particles.rmax, particles.y + particles.rmax],
        [paritcles.z - particles.rmax, particles.z + particles.rmax],
    ]

    swift_mask.constrain_spatial(spatial_mask)

    data = swiftsimio.load(snapshot_filename, mask=swift_mask)

    if not generate_extra_mask:
        return data

    # Now we must generate the secondary mask, for all available
    # particle types.

    particle_name_masks = {}

    for particle_name in data.metadata.present_particle_names:
        # This will change if we ever take advantage of the
        # parttypes available through velociraptor.
        particle_name_masks[particle_name] = np.in1d(
            getattr(data, particle_name).particle_ids, particles.particle_ids
        )

    # Finally we generate a named tuple with the correct fields and
    # fill it with the contents of our dictionary
    MaskTuple = namedtuple("MaskCollection", data.metadata.present_particle_names)
    mask = MaskTuple(**particle_name_masks)

    return data, mask
