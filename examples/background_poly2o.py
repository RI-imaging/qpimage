"""Background image 2nd order polynomial correction

This example extends the tilt correction ('background_tilt.py') to
a second order polynomial correction for samples that exhibit
more sophisticated phase aberrations. The phase background correction
is computed from a ten pixel wide frame around the image.
The phase data shown are computed from a hologram of a single
myeloid leukemia cell (HL60) recorded using digital holographic
microscopy (DHM) (see :cite:`Schuermann2015`).
"""
import matplotlib.pylab as plt
import numpy as np
# The data are stored in a .jpg file (lossy compression).
# If `PIL` is not found, try installing the `pillow` package.
from PIL import Image
import qpimage

edata = np.array(Image.open("./data/hologram_cell_curved_bg.jpg"))

# create QPImage instance
qpi = qpimage.QPImage(data=edata, which_data="hologram")
pha0 = qpi.pha

# background correction using tilt only
qpi.compute_bg(which_data=["phase"],
               fit_offset="fit",
               fit_profile="tilt",
               border_px=10,
               )
pha_tilt = qpi.pha

# background correction using polynomial
qpi.compute_bg(which_data=["phase"],
               fit_offset="fit",
               fit_profile="poly2o",
               border_px=10,
               )
pha_poly2o = qpi.pha

# plot phase data
fig = plt.figure(figsize=(8, 3.3))

phakw = {"cmap": "viridis",
         "interpolation": "bicubic",
         "vmin": pha_poly2o.min(),
         "vmax": pha_poly2o.max()}

ax1 = plt.subplot(131, title="input phase")
map1 = ax1.imshow(pha0, **phakw)
plt.colorbar(map1, ax=ax1, fraction=.067, pad=0.04)

ax2 = plt.subplot(132, title="tilt correction only")
map2 = ax2.imshow(pha_tilt, **phakw)
plt.colorbar(map2, ax=ax2, fraction=.067, pad=0.04)

ax3 = plt.subplot(133, title="polynomial correction")
map3 = ax3.imshow(pha_poly2o, **phakw)
plt.colorbar(map3, ax=ax3, fraction=.067, pad=0.04)

# disable axes
[ax.axis("off") for ax in [ax1, ax2, ax3]]

plt.tight_layout(w_pad=0)
plt.show()
