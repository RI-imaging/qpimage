"""Hologram filter choice

There are several parameters that influence the quality of
phase and amplitude data retrieved from holograms. This example
demonstrates the advantages and disadvantages of a three
hologram filters in qpimage. For more information, please have
a look at :func:`qpimage.holo.get_field`.

Several observations can be made:

- There appears to be a "bleed-through" of phase data into the
  amplitude data.
- A (sharp) disk filter introduces ringing artifacts in the amplitude
  and phase images.
- A smooth disk filter does not lead to such artifacts, but a dark
  halo is introduced around the coins in the amplitude image.
- The amplitude reconstruction with the gaussian filter does not
  exhibit the dark halo but, due to blurring, reveals less details.

To correctly interpret the data shown, please note that:

- This is a simulated hologram with *no* central band. For real
  data, the "filter_size" parameter also affects the reconstruction
  quality. Contributions from the central band can lead to strong
  artifacts. A balance between high resolution (large filter size)
  and small contributions from the central band (small filter size)
  usually has be found.
- It is not trivial to compare a gaussian filter with a disk filter
  in terms of filter size (sigma vs. radius).
  The gaussian filter takes into account larger frequencies and
  suppresses low frequencies. In qpimage, the actual gaussian filter
  size is chosen such that the resolution approximately matches that
  of the disk filter with a corresponding radius. In general however,
  the filter size parameter has to be examined when comparing the two.
- There is an inherent loss of information (resolution) in the
  holographic reconstruction process. The side band is isolated with a
  low-pass filter in Fourier space. The size and shape of this filter
  determine the resolution of the phase and amplitude images. As a
  result, the level of detail of all reconstructions shown is lower
  than that of the original images.
"""
import matplotlib.pylab as plt
import numpy as np
import qpimage
from skimage import color, data

# image of a galaxy recorded with the Hubble telescope
img1 = color.rgb2grey(data.hubble_deep_field())[354:504, 70:220]
# image of a coin
img2 = color.rgb2grey(data.coins())[150:300, 70:220]

pha = img1/img1.max() * 2 * np.pi
amp = img2/img2.mean()

# create a hologram
x, y = np.mgrid[0:150, 0:150]
hologram = 2 * amp * np.cos(-2 * (x + y) + pha)

filters = ["disk", "smooth disk", "gauss"]
qpis = []

for filter_name in filters:
    qpi = qpimage.QPImage(data=hologram,
                          which_data="hologram",
                          holo_kw={"filter_size": .5,
                                   "filter_name": filter_name})
    qpis.append(qpi)

fig = plt.figure(figsize=(8, 16))

phakw = {"interpolation": "bicubic",
         "cmap": "viridis",
         "vmin": pha.min(),
         "vmax": pha.max(),
         }

ampkw = {"interpolation": "bicubic",
         "cmap": "gray",
         "vmin": amp.min(),
         "vmax": amp.max()
         }

numrows = len(filters) + 1

plt.subplot(numrows, 2, 1, title="original phase")
plt.imshow(pha, **phakw)

ax2 = plt.subplot(numrows, 2, 2, title="original amplitude")
plt.imshow(amp, **ampkw)

for ii in range(len(filters)):
    # phase
    plt.subplot(numrows, 2, 2*ii+3, title=filters[ii]+" filter")
    plt.imshow(qpis[ii].pha, **phakw)
    # amplitude
    plt.subplot(numrows, 2, 2*ii+4, title=filters[ii]+" filter")
    plt.imshow(qpis[ii].amp, **ampkw)

# disable axes
for ax in fig.get_axes():
    ax.axis("off")

plt.tight_layout()
plt.show()
