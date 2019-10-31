"""
An example script showing the `swiftsimio` integration of
the velociraptor library.

Give it the snapshot path as the first arugment, and the
velociraptor base name (i.e. without any 'groups' or
'properties' and no dot) as the second.

This then creates a rotating visualisation movie of a selected
halo (the third argument).
"""

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from velociraptor.swift.swift import to_swiftsimio_dataset
from velociraptor.particles import load_groups
from velociraptor import load
from swiftsimio.visualisation.sphviewer import SPHViewerWrapper
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation

import sys

snapshot_path = sys.argv[1]
velociraptor_base_name = sys.argv[2]
halo_id = int(sys.argv[3])

# Instantiate main velociraptor objects
velociraptor_properties = f"{velociraptor_base_name}.properties"
velociraptor_groups = f"{velociraptor_base_name}.catalog_groups"

catalogue = load(velociraptor_properties)
groups = load_groups(velociraptor_groups, catalogue)

# This allows us to extract a siwftsimio dataset containing
# only the (spatially selected) particles around a halo
particles, unbound_particles = groups.extract_halo(halo_id)
data = to_swiftsimio_dataset(particles, snapshot_path, generate_extra_mask=False)

# Velociraptor stores these as physical, so we need to convert them back to comoving
x = particles.x_star / data.metadata.a
y = particles.y_star / data.metadata.a
z = particles.z_star / data.metadata.a
r_size = particles.r_size * 0.6 / data.metadata.a

# Use the sphviewer integration in swiftsimio to perform the rendering
sphviewer = SPHViewerWrapper(data.gas)


def update_sphviewer(sphviewer: SPHViewerWrapper, angle=0) -> SPHViewerWrapper:
    """
    Update the SPHViewerWrapper instance with a new rotation
    angle, and render the image at that angle.
    """
    sphviewer.get_camera(
        x=x, y=y, z=z, zoom=2, xsize=1024, ysize=1024, r=r_size, p=angle
    )

    sphviewer.get_scene()
    sphviewer.get_render()

    return sphviewer


# Finally, set up the actual plotting code.
fig, ax = plt.subplots(figsize=(8, 8), dpi=1024 // 8)
fig.subplots_adjust(0, 0, 1, 1)
ax.axis("off")

sphviewer = update_sphviewer(sphviewer, angle=0)
norm = LogNorm(vmin=sphviewer.image.min(), vmax=sphviewer.image.max())
image = ax.imshow(sphviewer.image, norm=norm, cmap="RdBu_r", origin="lower")

ax.text(
    0.975,
    0.975,
    f"$z={data.metadata.z:3.3f}$",
    color="white",
    ha="right",
    va="top",
    transform=ax.transAxes,
)


def frame(angle):
    update_sphviewer(sphviewer, angle=angle)
    image.set_array(sphviewer.image)

    return


# Render the animation and quit!
fa = FuncAnimation(fig, frame, tqdm(np.arange(360)), fargs=[], interval=1000 / 25)

fa.save(f"out_{halo_id}.mp4")
