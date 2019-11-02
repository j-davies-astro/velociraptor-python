"""
An example script showing the `swiftsimio` integration of
the velociraptor library.
"""

import matplotlib.pyplot as plt
import numpy as np
import unyt

from tqdm import tqdm
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation

from velociraptor.swift.swift import to_swiftsimio_dataset
from velociraptor.particles import load_groups
from velociraptor import load
from swiftsimio.visualisation.sphviewer import SPHViewerWrapper

from typing import Union

import argparse as ap

parser = ap.ArgumentParser(
    description="Create a rotation movie around a specified halo"
)

parser.add_argument(
    "-s", "--snap", help="Snapshot location. Required.", required=True, type=str
)

parser.add_argument(
    "-v",
    "--velociraptor",
    help="Velociraptor base name, i.e. without the file extension. Required.",
    required=True,
    type=str,
)

parser.add_argument(
    "-i", "--id", help="Halo ID to visualise. Required.", required=True, type=int
)

parser.add_argument(
    "-r",
    "--resolution",
    help="Resolution of the output video. Default: 1920.",
    required=False,
    default=1920,
    type=int,
)

parser.add_argument(
    "-p",
    "--property",
    help="Property to smooth over. Default: masses.",
    required=False,
    default="masses",
    type=str,
)

parser.add_argument(
    "-c",
    "--cmap",
    help="Colour map to use. Default: RdBu_r.",
    required=False,
    default="RdBu_r",
    type=str,
)

parser.add_argument(
    "-n",
    "--nframes",
    help="Number of frames to generate in the 360 degree rotation. Default: 360.",
    required=False,
    default=360,
    type=int,
)

args = vars(parser.parse_args())

snapshot_path = args["snap"]
velociraptor_base_name = args["velociraptor"]
halo_id = args["id"]
resolution = args["resolution"]
smooth_over = args["property"]
cmap = args["cmap"]
n_frames = args["nframes"]

# Generate the frame numbers we're actually going to use.
step = 360 / n_frames
# This is better than linspace as it ensures things wrap properly
frames = np.arange(0, 360, step)

# Instantiate main velociraptor objects
velociraptor_properties = f"{velociraptor_base_name}.properties"
velociraptor_groups = f"{velociraptor_base_name}.catalog_groups"

catalogue = load(velociraptor_properties)
groups = load_groups(velociraptor_groups, catalogue)

# This allows us to extract a siwftsimio dataset containing
# only the (spatially selected) particles around a halo
particles, unbound_particles = groups.extract_halo(halo_id)
data = to_swiftsimio_dataset(particles, snapshot_path, generate_extra_mask=False)

# Velociraptor stores these as physical, so we need to convert them back to comoving.
# Focus around the most bound particle.
x = particles.x_mbp / data.metadata.a
y = particles.y_mbp / data.metadata.a
z = particles.z_mbp / data.metadata.a
r_size = particles.r_size * 1.0 / data.metadata.a

# Use the sphviewer integration in swiftsimio to perform the rendering
smooth_over_dataset = getattr(data.gas, smooth_over)
smooth_over_dataset[smooth_over_dataset < 0 * smooth_over_dataset.units] = (
    0.0 * smooth_over_dataset.units
)

sphviewer = SPHViewerWrapper(data.gas, smooth_over=smooth_over)

if smooth_over != "masses":
    sphviewer_norm = SPHViewerWrapper(
        data.gas,
        smooth_over=unyt.unyt_array(np.ones(data.metadata.n_gas), unyt.dimensionless),
    )
else:
    sphviewer_norm = None


def update_sphviewer(
    sphviewer: SPHViewerWrapper,
    sphviewer_norm: Union[SPHViewerWrapper, None] = None,
    angle=0,
) -> SPHViewerWrapper:
    """
    Update the image (which is returned) by modifying the sphviewer and
    sphviewer norm objects.
    """

    update_camera_props = dict(
        x=x, y=y, z=z, zoom=2, xsize=resolution, ysize=resolution, r=r_size, p=angle
    )

    sphviewer.get_camera(**update_camera_props)

    sphviewer.get_scene()
    sphviewer.get_render()

    if sphviewer_norm is not None:
        sphviewer_norm.get_camera(**update_camera_props)
        sphviewer_norm.get_scene()
        sphviewer_norm.get_render()

        return (sphviewer.image / sphviewer_norm.image).value
    else:
        return (sphviewer.image).value


# Finally, set up the actual plotting code.
fig, ax = plt.subplots(figsize=(8, 8), dpi=resolution // 8)
fig.subplots_adjust(0, 0, 1, 1)
ax.axis("off")

this_frame = update_sphviewer(sphviewer, angle=0)
norm = LogNorm(vmin=this_frame.min(), vmax=this_frame.max())
image = ax.imshow(this_frame, norm=norm, cmap=cmap, origin="lower")

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
    this_frame = update_sphviewer(sphviewer, sphviewer_norm, angle=angle)
    image.set_array(this_frame)

    return


# Render the animation and quit!
fa = FuncAnimation(fig, frame, tqdm(frames), fargs=[], interval=1000 / 25)

fa.save(f"out_{halo_id}_{smooth_over}.mp4")
