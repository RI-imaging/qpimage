"""Background image offset correction

This example illustrates the different background offset
correction methods implemented in qpimage. The phase image
data contains two gaussian noise distributions for which
these methods yield different background phase offsets.
"""
import matplotlib.pylab as plt
import numpy as np
import qpimage

size = 200  # the size of the image
bg = 2.5  # the center of the background phase distribution
scale = .1  # the spread of the background phase distribution

# compute random phase data
rsobj = np.random.RandomState(42)
data = rsobj.normal(loc=bg, scale=scale, size=size**2)
# Add a second distribution `data2` at random positions `idx`,
# such that there is no pure gaussian distribution.
# (otherwise 'mean' and 'gaussian' cannot be distinguished)
data2 = rsobj.normal(loc=bg*1.1, scale=scale, size=size**2//2)
idx = rsobj.choice(data.size, data.size//2)
data[idx] = data2
# reshape `data` to get a 2D array
data = data.reshape(size, size)

qpi = qpimage.QPImage(data=data, which_data="phase")

cpkw = {"which_data": "phase",  # correct the input phase data
        "fit_profile": "offset",  # perform offset correction only
        "border_px": 5,  # use a border of 5px of the input phase
        "ret_mask": True,  # return the mask image for visualization
        }

mask = qpi.compute_bg(fit_offset="mode", **cpkw)
bg_mode = np.mean(qpi.bg_pha[mask])

qpi.compute_bg(fit_offset="mean", **cpkw)
bg_mean = np.mean(qpi.bg_pha[mask])

qpi.compute_bg(fit_offset="gauss", **cpkw)
bg_gauss = np.mean(qpi.bg_pha[mask])

bg_data = (qpi.pha + qpi.bg_pha)[mask]
# compute histogram
nbins = int(np.ceil(np.sqrt(bg_data.size)))
mind, maxd = bg_data.min(), bg_data.max()
histo = np.histogram(bg_data, nbins, density=True, range=(mind, maxd))
dx = abs(histo[1][1] - histo[1][2]) / 2
hx = histo[1][1:] - dx
hy = histo[0]

# plot the properties of `qpi`
plt.figure(figsize=(8, 4))

ax1 = plt.subplot(121, title="input phase")
map1 = plt.imshow(data)
plt.colorbar(map1, ax=ax1, fraction=.046, pad=0.04)


t2 = "{}px border histogram with {} bins".format(cpkw["border_px"], nbins)
plt.subplot(122, title=t2)
plt.plot(hx, hy, label="histogram", color="gray")
plt.axvline(bg_mode, 0, 1, label="mode", color="red")
plt.axvline(bg_mean, 0, 1, label="mean", color="green")
plt.axvline(bg_gauss, 0, 1, label="gauss", color="orange")
plt.legend()

plt.tight_layout()
plt.show()
