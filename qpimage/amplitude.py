import numpy as np


class Amplitude(object):
    def __init__(self, data):
        data.setflags(write=False)
        self.raw = data

    def set_bg(self, bg):
        assert isinstance(bg, (float, int, Amplitude))
        if isinstance(bg, Amplitude):
            bg = bg.raw
        if isinstance(bg, np.ndarray):
            bg.setflags(write=False)
        self.bg = bg
