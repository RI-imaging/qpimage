"""Digital hologram of a single cell

This example illustrates how qpimage can be used to analyze
digital holograms. The hologram of a single myeloid leukemia
cell (HL60) shown was recorded using digital holographic microscopy
(DHM). Because the phase-retrieval method used in DHM is based on the
discrete Fourier transform, there always is a residual background
phase tilt which must be removed for further image analysis.
The setup used for recording these data is described in reference
:cite:`Schuermann2015`, which also contains a description of the
hologram-to-phase conversion and phase background correction algorithms
which qpimage is based on.
"""
import matplotlib
import matplotlib.pylab as plt
import numpy as np
import qpimage

# load the experimental data
edata = np.load("./data/hologram_cell.npz")

# create QPImage instance
qpi = qpimage.QPImage(data=edata["data"],
                      bg_data=edata["bg_data"],
                      which_data="hologram",
                      # This parameter allows to pass arguments to the
                      # hologram-analysis algorithm of qpimage.
                      # (see qpimage.holo.get_field)
                      holo_kw={
                               # For this hologram, the "smooth disk"
                               # filter yields the best trade-off
                               # between interference from the central
                               # band and image resolution.
                               "filter_name": "smooth disk",
                               # As can be seen in the hologram image,
                               # the sidebands are not positioned at
                               # an angle of 45° from the central band.
                               # If the filter size is 1/3 (default),
                               # the central band introduces line-
                               # artifacts to the reconstructed image.
                               "filter_size": 1/4
                               }
                      )

amp0 = qpi.amp
pha0 = qpi.pha

# background correction
qpi.compute_bg(which_data=["amplitude", "phase"],
               fit_offset="fit",
               fit_profile="tilt",
               border_px=5,
               )

# plot the properties of `qpi`
fig = plt.figure(figsize=(8, 10))

matplotlib.rcParams["image.interpolation"] = "bicubic"
holkw = {"cmap": "gray",
         "vmin": 0,
         "vmax": 200}

ax1 = plt.subplot(321, title="cell hologram")
map1 = ax1.imshow(edata["data"], **holkw)
plt.colorbar(map1, ax=ax1, fraction=.046, pad=0.04)

ax2 = plt.subplot(322, title="bg hologram")
map2 = ax2.imshow(edata["bg_data"], **holkw)
plt.colorbar(map2, ax=ax2, fraction=.046, pad=0.04)

ax3 = plt.subplot(323, title="input phase [rad]")
map3 = ax3.imshow(pha0)
plt.colorbar(map3, ax=ax3, fraction=.046, pad=0.04)

ax4 = plt.subplot(324, title="input amplitude")
map4 = ax4.imshow(amp0, cmap="gray")
plt.colorbar(map4, ax=ax4, fraction=.046, pad=0.04)

ax5 = plt.subplot(325, title="corrected phase [rad]")
map5 = ax5.imshow(qpi.pha)
plt.colorbar(map5, ax=ax5, fraction=.046, pad=0.04)

ax6 = plt.subplot(326, title="corrected amplitude")
map6 = ax6.imshow(qpi.amp, cmap="gray")
plt.colorbar(map6, ax=ax6, fraction=.046, pad=0.04)

# disable axes
[ax.axis("off") for ax in [ax1, ax2, ax3, ax4, ax5, ax6]]

plt.tight_layout()
plt.show()
