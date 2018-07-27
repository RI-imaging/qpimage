"""Object-mask background image correction

In some cases, using :ref:`only the border of the phase image
<example_background_poly2o>` for background correction
might not be enough. To increase the area of the background image,
it is possible to mask only the cell area. The :ref:`qpsphere package
<qpsphere:index>` provides the convenience method
:func:`qpsphere.cnvnc.bg_phase_mask_for_qpi` which computes
the background phase mask based on the position and radius of an
automatically detected spherical phase object. The sized of the
mask can be tuned with the `radial_clearance` parameter.

Note that the various methods used in the examples for determining
such a phase mask can be combined. Also note that before
applying the method discussed here, an initial background correction
might be necessary.
"""
import matplotlib.pylab as plt
import numpy as np
# The data are stored in a .jpg file (lossy compression).
# If `PIL` is not found, try installing the `pillow` package.
from PIL import Image
import qpimage
import qpsphere

edata = np.array(Image.open("./data/hologram_cell_curved_bg.jpg"))

# create QPImage instance
qpi = qpimage.QPImage(data=edata,
                      which_data="hologram",
                      meta_data={"medium index": 1.335,
                                 "wavelength": 550e-9,
                                 "pixel size": 0.107e-6})
pha0 = qpi.pha

# determine the position of the cell (takes a while)
mask = qpsphere.cnvnc.bg_phase_mask_for_qpi(qpi=qpi,
                                            r0=7e-6,
                                            method="edge",
                                            model="projection",
                                            radial_clearance=1.15)

# background correction using polynomial and mask
qpi.compute_bg(which_data=["phase"],
               fit_offset="fit",
               fit_profile="poly2o",
               from_mask=mask,
               )
pha_corr = qpi.pha

# plot phase data
fig = plt.figure(figsize=(8, 3.3))

phakw = {"cmap": "viridis",
         "interpolation": "bicubic",
         "vmin": pha_corr.min(),
         "vmax": pha_corr.max()}

ax1 = plt.subplot(131, title="input phase")
map1 = ax1.imshow(pha0, **phakw)
plt.colorbar(map1, ax=ax1, fraction=.067, pad=0.04)

ax2 = plt.subplot(132, title="background phase mask")
map2 = ax2.imshow(1.*mask, cmap="gray_r")
plt.colorbar(map2, ax=ax2, fraction=.067, pad=0.04)

ax3 = plt.subplot(133, title="polynomial correction")
map3 = ax3.imshow(pha_corr, **phakw)
plt.colorbar(map3, ax=ax3, fraction=.067, pad=0.04)

# disable axes
[ax.axis("off") for ax in [ax1, ax2, ax3]]

plt.tight_layout(w_pad=0)
plt.show()
