#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import math
import random

# defining constants
MAX_INT = 2147483647



class PulsingCircleAnimation:
    def __init__(self, animationController):
        # animation settings
        self.centerPositionX = 2
        self.centerPositionY = 2
        self.distanceToDarkness = 3.25 # 2.8 is exact radius to corners
        self.speedFactor = 40
        self.amplitudeFactor = 0.15 # amplitude = 2 * amplitudeFactor; range [0, 0.5]
        self.wavePosition = self.amplitudeFactor + 0.01 # for max orientation `(1 - amplitude)`, `amplitude` for min orientation
        self.iterationStep = 0

         # initializations
        self.animationController = animationController
        self.colorCalculator = animationController.colorCalculator
        self.device = self.animationController.getDevice()

    def renderNextFrame(self):
        # handle iteration counting and limit it to maxint
        if self.iterationStep < MAX_INT:
            self.iterationStep = self.iterationStep + 1
        else:
            self.iterationStep = 0

        for x in range(0, 5):
            for y in range(0, 5):
                brightness = self.circleIntensity(x, y, self.centerPositionX, self.centerPositionY)
                hexColor = self.colorCalculator.setBrightnessToHexColor(self.animationController.getBasisColor(), brightness)
                self.device.setHexColorToBufferForLedWithCoordinates(hexColor, x, y)

    def circleIntensity(self, x, y, xPosition = 2, yPosition = 2):
        x = x - xPosition
        y = y - yPosition

        intermediateStep = math.sqrt((x * x) + (y * y)) / (self.distanceToDarkness / math.pi)
        return (math.cos(intermediateStep + (- self.iterationStep / self.speedFactor)) * self.amplitudeFactor) + self.wavePosition
