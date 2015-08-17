#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import project libs
from colorCalculator import ColorCalculator
from colorController import ColorController
from issetHelper import IssetHelper



class ColorChange(IssetHelper):

    def __init__(self, device):
        # initializations
        self.device = device
        self.colors = ColorController
        self.colorCalculator = ColorCalculator()
        self.hueAdditionPerFrame = 0.0

        # animation settings
        self.currentHueAddition = 0.0
        self.speed = 10

    def start(self):
        self.hueAdditionPerFrame = 0.00001 * (self.speed + 1)

    def renderNextFrame(self):
        (currentHue, saturation, lightness) = self.colors.getBasisColorAsHsl()
        targetHue = self.colorCalculator.correctHueValue(
            currentHue + self.hueAdditionPerFrame)

        self.colors.setBasisColorAsHsl(targetHue, saturation, lightness)
        (r, g, b) = self.colors.getBasisColorAsRgb()
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
