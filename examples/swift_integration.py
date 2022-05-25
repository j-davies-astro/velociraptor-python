"""
An example script showing the `swiftsimio` integration of
the velociraptor library.

Give it the snapshot path as the first arugment, and the
velociraptor base name (i.e. without any 'groups' or
'properties' and no dot) as the second.
"""

from velociraptor.swift.swift import to_swiftsimio_dataset
from velociraptor.particles import load_groups
from velociraptor import load

from tqdm import tqdm

import sys

snapshot_path = sys.argv[1]
velociraptor_base_name = sys.argv[2]
halo_ids = range(0, 100)

velociraptor_properties = f"{velociraptor_base_name}.properties"
velociraptor_groups = f"{velociraptor_base_name}.catalog_groups"

catalogue = load(velociraptor_properties)
groups = load_groups(velociraptor_groups, catalogue)

# Let's make an image of those particles!
import matplotlib.pyplot as plt
import numpy as np

from swiftsimio.visualisation.sphviewer import SPHViewerWrapper
from matplotlib.colors import LogNorm

for halo_id in tqdm(halo_ids):
    particles, unbound_particles = groups.extract_halo(halo_id)

    # This reads particles using the cell metadata that are around our halo
    data = to_swiftsimio_dataset(particles, snapshot_path, generate_extra_mask=False)

    for particle_type in data.metadata.present_particle_names:
        particle_data = getattr(data, particle_type)
        sphviewer = SPHViewerWrapper(particle_data)

        x = particles.x / data.metadata.a
        y = particles.y / data.metadata.a
        z = particles.z / data.metadata.a
        r_size = particles.r_size * 0.8 / data.metadata.a

        # This gets an SPHViewer render from our swiftsimio dataset
        sphviewer.get_camera(x=x, y=y, z=z, r=r_size, zoom=2, xsize=1024, ysize=1024)
        sphviewer.get_scene()
        sphviewer.get_render()

        fig, ax = plt.subplots(figsize=(8, 8), dpi=1024 // 8)
        fig.subplots_adjust(0, 0, 1, 1)
        ax.axis("off")

        ax.imshow(sphviewer.image.value, norm=LogNorm(), cmap="RdBu_r", origin="lower")
        ax.text(
            0.975,
            0.975,
            f"$z={data.metadata.z:3.3f}$",
            color="white",
            ha="right",
            va="top",
            transform=ax.transAxes,
        )

        fig.savefig(f"{particle_type}_halo_image_{halo_id}.png")

        plt.close(fig)
