"""Masked background image correction

This example illustrates background correction with qpimage using
a mask to exclude regions that do not contain background
information.

The phase image of a microgel bead (top left) has two artifacts; there
is a tilt-like phase profile added along the vertical axis and there is
a second microgel bead in close proximity to the center bead. A regular
phase tilt background correction using the image values around a frame
of five pixels (see "background_tilt.py" example) does not yield a flat
background, because the second bead is fitted into the background which
leads to a horizontal background phase profile (top right). By defining
a mask (bottom left image), the phase values of the second bead
can be excluded from the background tilt fit and a flat background
phase is achieved (bottom right).
"""
import matplotlib.pylab as plt
import numpy as np
import qpimage


# load the experimental data
input_phase = np.load("./data/phase_beads_close.npz")["phase"].astype(float)

# create QPImage instance
qpi = qpimage.QPImage(data=input_phase,
                      which_data="phase")

# background correction without mask
qpi.compute_bg(which_data="phase",
               fit_offset="fit",
               fit_profile="tilt",
               border_px=5,
               )
pha_nomask = qpi.pha

# educated guess for mask
mask = input_phase < input_phase.max() / 10

# background correction with mask
# (the intersection of `mask` and the 5px border is used for fitting)
qpi.compute_bg(which_data="phase",
               fit_offset="fit",
               fit_profile="tilt",
               border_px=5,
               from_mask=mask
               )
pha_mask = qpi.pha

# plot
fig = plt.figure(figsize=(8, 7))
plot_kw = {"vmin": -.1,
           "vmax": 1.5}

ax1 = plt.subplot(221, title="input phase")
map1 = ax1.imshow(input_phase, **plot_kw)
plt.colorbar(map1, ax=ax1, fraction=.044, pad=0.04)

ax2 = plt.subplot(222, title="tilt-corrected (no mask)")
map2 = ax2.imshow(pha_nomask, **plot_kw)
plt.colorbar(map2, ax=ax2, fraction=.044, pad=0.04)

ax3 = plt.subplot(223, title="mask")
map3 = ax3.imshow(1.*mask, cmap="gray_r")
plt.colorbar(map3, ax=ax3, fraction=.044, pad=0.04)

ax4 = plt.subplot(224, title="tilt-corrected (with mask)")
map4 = ax4.imshow(pha_mask, **plot_kw)
plt.colorbar(map4, ax=ax4, fraction=.044, pad=0.04)

# disable axes
[ax.axis("off") for ax in [ax1, ax2, ax3, ax3, ax4]]

plt.tight_layout(h_pad=0, w_pad=0)
plt.show()
