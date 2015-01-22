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
        self.centerPositionY = 5
        self.distanceToDarkness = 3.25 # 2.8 is exact radius to corners
        self.speed = 40
        self.amplitude = 0.3 # range [0, 1]
        self.wavePosition = 0.16
        self.iterationStep = 0

        # initializations
        self.animationController = animationController
        self.colorCalculator = animationController.colorCalculator
        self.device = self.animationController.getDevice()

        # construct array of precalculated values
        self.cosSummands = [[0.0 for x in range(self.device.getNumberOfLeds())] for x in range(self.device.getNumberOfLeds())] 

    def start(self):
        # precalculated values
        self.amplitudeFactor = self.amplitude / 2
        self.speedFactor = 1 / self.speed

        # calculate values for each pixel position
        for i in range(0, self.device.getNumberOfLeds()):
            for j in range(0, self.device.getNumberOfLeds()):
                x = i - self.centerPositionX
                y = j - self.centerPositionY
                self.cosSummands[i][j] = (math.sqrt((x * x) + (y * y)) * math.pi) / self.distanceToDarkness

    def renderNextFrame(self):
        # handle iteration counting and limit it to maxint
        if self.iterationStep < MAX_INT:
            self.iterationStep = self.iterationStep + 1
        else:
            self.iterationStep = 0

        for x in range(0, 5):
            for y in range(0, 5):
                brightness = self.circleIntensity(x, y)
                hexColor = self.colorCalculator.setBrightnessToHexColor(self.animationController.getBasisColor(), brightness)
                self.device.setHexColorToBufferForLedWithCoordinates(hexColor, x, y)

    def circleIntensity(self, x, y):
        intermediateStep = math.cos(self.cosSummands[x][y] - (self.iterationStep * self.speedFactor))
        return (intermediateStep * self.amplitudeFactor) + self.wavePosition
