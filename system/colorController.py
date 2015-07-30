#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import project libs
from colorCalculator import ColorCalculator

# defining constants
ORANGE = 0xff4200
WHITE = 0xffffff



class _ColorController:
    def __call__(self):
        return self

    def __init__(self):
        # initializations
        self.device = None
        self.colorCalculator = ColorCalculator()
        self.basisColor = ORANGE
        self.binaryClockColor = WHITE
        self.basisLightness = 0.50
        self.binaryClockLightness = 1

        # value predefinitions
        self.basisHue = 0
        self.basisSaturation = 1
        self.basisRedChannel = 0
        self.basisGreenChannel = 0
        self.basisBlueChannel = 0
        self.binaryClockColorRedChannel = 0
        self.binaryClockColorGreenChannel = 0
        self.binaryClockColorBlueChannel = 0

        # calculate variations of initial color
        self.calculateVariationsOfBasisValues()

    def setDeviceReference(self, device):
        self.device = device

    # ***** value calculation **********************************
    def calculateVariationsOfBasisValues(self):
        self.calculateBasisColorValuesFomHex()
        self.calculateBinaryClockColorValuesFromHex()

    def calculateBasisColorValuesFomHex(self):
        (bHue, bSaturation, bLightness) = self.colorCalculator.convertHexColorToHSL(self.basisColor)
        (bR, bG, bB) = self.colorCalculator.convertHexColorToRgb(self.basisColor)
        self.basisHue = bHue
        self.basisSaturation = bSaturation
        self.basisLightness = bLightness
        self.basisRedChannel = bR
        self.basisGreenChannel = bG
        self.basisBlueChannel = bB

    def calculateBasisColorValuesFomRgb(self):
        self.basisColor = self.colorCalculator.convertRgbToHexColor(self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)
        (bHue, bSaturation, bLightness) = self.colorCalculator.convertRgbToHsl(self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)
        self.basisHue = bHue
        self.basisSaturation = bSaturation
        self.basisLightness = bLightness

    def calculateBasisColorValuesFomHsl(self):
        (bR, bG, bB) = self.colorCalculator.convertHslToRgb(self.basisHue, self.basisSaturation, self.basisLightness)
        self.basisColor = self.colorCalculator.convertRgbToHexColor(bR, bG, bB)
        self.basisRedChannel = bR
        self.basisGreenChannel = bG
        self.basisBlueChannel = bB

    def calculateBinaryClockColorValuesFromHex(self):
        (r, g, b) = self.colorCalculator.convertHexColorToRgb(self.binaryClockColor)
        self.binaryClockColorRedChannel = r
        self.binaryClockColorGreenChannel = g
        self.binaryClockColorBlueChannel = b

    def calculateBinaryClockColorValuesFomRgb(self):
        self.binaryClockColor = self.colorCalculator.convertRgbToHexColor(self.binaryClockColorRedChannel, self.binaryClockColorGreenChannel, self.binaryClockColorBlueChannel)

    # ***** getter **********************************
    def getBasisColorAsHex(self):
        return self.colorCalculator.getHtmlHexStringFromRgbColor(self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)

    def getBasisColorAsRgb(self):
        return (self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)

    def getBasisColorAsHsl(self):
        return (self.basisHue, self.basisSaturation, self.basisLightness)

    def getBasisLightness(self):
        return self.basisLightness

    def getTotalLightness(self):
        numberOfLeds = self.device.getNumberOfLeds()
        totalLightness = 0

        for i in range(0, numberOfLeds):
            r, g, b = self.device.getRgbFromBufferWithIndex(i)
            totalLightness += self.colorCalculator.convertRgbToLightness(r, g, b)

        return totalLightness / numberOfLeds

    # ***** setter **********************************
    def setBasisColorAsHex(self, hexColor):
        self.basisColor = hexColor
        self.calculateBasisColorValuesFomHex()

    def setBasisColorAsRgb(self, redChannel, greenChannel, blueChannel):
        self.basisRedChannel = redChannel
        self.basisGreenChannel = greenChannel
        self.basisBlueChannel = blueChannel
        self.calculateBasisColorValuesFomRgb()

    def setBasisColorAsHsl(self, hue, saturation, lightness):
        self.basisHue = hue
        self.basisSaturation = saturation
        self.basisLightness = lightness
        self.calculateBasisColorValuesFomHsl()

    def setBinaryClockColorAsHex(self, hexColor):
        self.binaryClockColor = hexColor
        self.calculateBinaryClockColorValuesFromHex()

    def setBinaryClockColorAsRgb(self, redChannel, greenChannel, blueChannel):
        self.binaryClockColorRedChannel = redChannel
        self.binaryClockColorGreenChannel = greenChannel
        self.binaryClockColorBlueChannel = blueChannel
        self.calculateBinaryClockColorValuesFomRgb()

    def setBasisLightness(self, lightness):
        if lightness > 1:
            lightness = 1
        elif lightness < 0:
            lightness = 0

        self.basisLightness = lightness
        self.setBasisColorAsHsl(self.basisHue, self.basisSaturation, lightness)

    def setBinaryClockLightness(self, lightness):
        if lightness > 1:
            lightness = 1
        elif lightness < 0:
            lightness = 0

        self.binaryClockLightness = lightness
        self.setBinaryClockColorAsHex(self.colorCalculator.setBrightnessToHexColor(self.binaryClockColor, lightness))

ColorController = _ColorController()
del _ColorController
