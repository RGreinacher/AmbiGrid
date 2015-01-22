#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
from array import array
import math

# defining constants
MAX_INT = 2147483647



class PulsingCircleAnimation:
    def __init__(self, animationController):
        # animation settings
        self.centerPositionX = 0
        self.centerPositionY = 4
        self.degreeOfColorDivergence = 20
        self.distanceToDarkness = 3.25 # 2.8 is exact radius to corners
        self.speed = 40
        self.amplitude = 0.3 # range [0, 1]
        self.wavePosition = self.amplitude / 2 + 0.005
        self.iterationStep = 0

        # initializations
        self.animationController = animationController
        self.colorCalculator = animationController.colorCalculator
        self.device = self.animationController.getDevice()
        (self.basisHue, self.basisSaturation, self.basisLightness) = self.colorCalculator.convertHexToHSL(self.animationController.getBasisColor())

        # construct array of precalculated values
        self.sinSummands = [[0.0 for x in range(self.device.getNumberOfLeds())] for x in range(self.device.getNumberOfLeds())] 

    def start(self):
        # precalculated values
        self.amplitudeFactor = self.amplitude / 2
        self.speedFactor = 1 / self.speed
        self.degreeFactor = ((self.degreeOfColorDivergence / 360) / 2)

        # calculate values for each pixel position
        for i in range(0, self.device.getNumberOfLeds()):
            for j in range(0, self.device.getNumberOfLeds()):
                x = i - self.centerPositionX
                y = j - self.centerPositionY
                self.sinSummands[i][j] = (math.sqrt((x * x) + (y * y)) * math.pi) / self.distanceToDarkness

    def renderNextFrame(self):
        # handle iteration counting and limit it to maxint
        if self.iterationStep < MAX_INT:
            self.iterationStep = self.iterationStep + 1
        else:
            self.iterationStep = 0

        for x in range(0, 5):
            for y in range(0, 5):
                # intensity = self.circleIntensity(x, y)
                # get current color
                (r, g, b) = self.device.getRgbFromBufferWithCoordinates(x, y)
                (h, s, l) = self.colorCalculator.convertRgbToHsl(r, g, b)

                (hueAddition, newLightness) = self.getColorForCoordinates(x, y)
                (r, g, b) = self.colorCalculator.convertHslToRgb(self.basisHue + hueAddition, self.basisSaturation, newLightness)
                self.device.setRgbColorToBufferForLedWithCoordinates(r, g, b, x, y)

                # brightness = intensity + self.wavePosition
                # hue = 
                # hexColor = self.colorCalculator.setBrightnessToHexColor(self.animationController.getBasisColor(), brightness)
                # self.device.setHexColorToBufferForLedWithCoordinates(hexColor, x, y)

    def getColorForCoordinates(self, x, y):
        intensity = math.sin(self.sinSummands[x][y] - (self.iterationStep * self.speedFactor))

        newHue = intensity * self.degreeFactor
        newLightness = (intensity * self.amplitudeFactor) + self.wavePosition
        return (newHue, newLightness)

