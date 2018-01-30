"""Simple phase

This example illustrates the simple usage of the
:class:`qpimage.QPImage <qpimage.core.QPImage>` class for reading and
managing quantitative phase data. The attribute ``QPImage.pha`` yields
the background-corrected phase data and the attribute
``QPImage.bg_pha`` yields the background phase image.
"""
import matplotlib.pylab as plt
import numpy as np
import qpimage

size = 200
# background phase image with a tilt
bg = np.repeat(np.linspace(0, 1, size), size).reshape(size, size)
# phase image with random noise
phase = np.random.rand(size, size) + bg

# create QPImage instance
qpi = qpimage.QPImage(data=phase, bg_data=bg, which_data="phase")

# plot the properties of `qpi`
plt.figure(figsize=(8, 3))
plot_kw = {"vmin": -1,
           "vmax": 2}

plt.subplot(131, title="fake input phase")
plt.imshow(phase, **plot_kw)

plt.subplot(132, title="fake background phase")
plt.imshow(qpi.bg_pha, **plot_kw)

plt.subplot(133, title="corrected phase")
plt.imshow(qpi.pha, **plot_kw)

plt.tight_layout()
plt.show()
