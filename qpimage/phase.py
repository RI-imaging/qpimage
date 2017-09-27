import numpy as np


class Phase(object):
    def __init__(self, data):
        data.setflags(write=False)
        self.raw = data

    def set_bg(self, bg):
        assert isinstance(bg, (float, int, Phase))
        if isinstance(bg, Phase):
            bg = bg.raw
        if isinstance(bg, np.ndarray):
            bg.setflags(write=False)
        self.bg = bg
