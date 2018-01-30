"""Background image tilt correction

This example illustrates background tilt correction with qpimage.
In contrast to the 'simple_phase.py' example, the known background data
is not given to the :class:`qpimage.QPImage <qpimage.core.QPImage>`
class. In this particular example, the background tilt correction
achieves an error of about 1% which is sufficient in most quantitative
phase imaging applications.
"""
import matplotlib.pylab as plt
import numpy as np
import qpimage

size = 200
# background phase image with a tilt
bg = np.repeat(np.linspace(0, 1, size), size).reshape(size, size)
bg = .6 * bg - .8 * bg.transpose() + .2
# phase image with random noise
rsobj = np.random.RandomState(47)
phase = rsobj.rand(size, size) - .5 + bg

# create QPImage instance
qpi = qpimage.QPImage(data=phase, which_data="phase")
# compute background with 2d tilt approach
qpi.compute_bg(which_data="phase",  # correct phase image
               fit_offset="fit",  # use bg offset from tilt fit
               fit_profile="tilt",  # perform 2D tilt fit
               border_px=5,  # use 5 px border around image
               )

# plot the properties of `qpi`
fig = plt.figure(figsize=(8, 2.5))
plot_kw = {"vmin": -1,
           "vmax": 1}

ax1 = plt.subplot(131, title="input data")
map1 = ax1.imshow(phase, **plot_kw)
plt.colorbar(map1, ax=ax1, fraction=.046, pad=0.04)

ax2 = plt.subplot(132, title="tilt-corrected")
map2 = ax2.imshow(qpi.pha, **plot_kw)
plt.colorbar(map2, ax=ax2, fraction=.046, pad=0.04)

ax3 = plt.subplot(133, title="tilt error")
map3 = ax3.imshow(bg - qpi.bg_pha)
plt.colorbar(map3, ax=ax3, fraction=.046, pad=0.04)

# disable axes
[ax.axis("off") for ax in [ax1, ax2, ax3]]

plt.tight_layout(pad=0, h_pad=0, w_pad=0)
plt.show()
