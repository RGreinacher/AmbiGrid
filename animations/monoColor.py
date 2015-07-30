#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import project libs
from colorController import ColorController



class MonoColor:

    def __init__(self, device):
        # initializations
        self.device = device
        self.colors = ColorController

    def renderNextFrame(self):
        (r, g, b) = self.colors.getBasisColorAsRgb()
        self.device.setRgbToBuffer(r, g, b)
