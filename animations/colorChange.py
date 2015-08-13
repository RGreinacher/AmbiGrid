#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import project libs
from colorCalculator import ColorCalculator
from colorController import ColorController

# defining constants
HUE_CAHNGE_STEPS = 3600



class ColorChange:

    def __init__(self, device):
        # initializations
        self.device = device
        self.colors = ColorController
        self.colorCalculator = ColorCalculator()
        self.hueAdditionPerFrame = 0.0

        # animation settings
        self.currentHueAddition = 0.0
        self.speed = 50

    def start(self):
        self.hueAdditionPerFrame = 1 / (HUE_CAHNGE_STEPS / self.speed)

    def renderNextFrame(self):
        (currentHue, saturation, lightness) = self.colors.getBasisColorAsHsl()
        self.currentHueAddition = self.colorCalculator.correctHueValue(
            self.currentHueAddition + self.hueAdditionPerFrame)

        targetHue = self.colorCalculator.correctHueValue(
            currentHue + self.currentHueAddition)

        (r, g, b) = self.colorCalculator.convertHslToRgb(
            targetHue, saturation, lightness)
        self.device.setRgbToBuffer(r, g, b)

    # ***** getter **********************************

    def getAttributes(self):
        return { 'speed': self.speed }

    # ***** setter **********************************

    def setAttributes(self, attributes):
        if self.isset(attributes, 'speed'):
            speed = self.saveIntConvert(attributes['speed'])
            if speed >= 0:
                self.speed = speed
                self.start()
