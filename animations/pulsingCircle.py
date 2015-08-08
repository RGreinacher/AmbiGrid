#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import math

# import project libs
from colorCalculator import ColorCalculator
from colorController import ColorController
from issetHelper import IssetHelper

# defining constants
MAX_INT = 2147483647



class PulsingCircleAnimation(IssetHelper):

    def __init__(self, device):
        # animation settings
        self.centerPositionX = 1
        self.centerPositionY = 5
        self.degreeOfColorDivergence = 30
        self.distanceToDarkness = 3
        self.speed = 0.01
        self.iterationStep = 0

        # initializations
        self.colorCalculator = ColorCalculator()
        self.colors = ColorController
        self.device = device
        self.degreeFactor = 0

        # construct array of precalculated values
        self.sinSummands = [
            [
                0.0 for x in range(self.device.getNumberOfLeds())
            ] for x in range(self.device.getNumberOfLeds())
        ]

    def start(self):
        # precalculated values
        self.degreeFactor = ((self.degreeOfColorDivergence / 360) / 2)

        # calculate values for each pixel position
        for i in range(0, self.device.getNumberOfLeds()):
            for j in range(0, self.device.getNumberOfLeds()):
                x = i - self.centerPositionX
                y = j - self.centerPositionY
                self.sinSummands[i][j] = (
                    math.sqrt((x * x) + (y * y)) * math.pi) / self.distanceToDarkness

    def renderNextFrame(self):
        # handle iteration counting and limit it to maxint
        if self.iterationStep < MAX_INT:
            self.iterationStep = self.iterationStep + 1
        else:
            self.iterationStep = 0

        for x in range(0, 7):
            for y in range(0, 7):
                # calculate new hue and lightness for current frame
                (hueAddition, lightnessFactor) = self.getColorForCoordinates(
                    x, y)
                targetHue = self.colors.basisHue + hueAddition
                targetLightness = self.colors.basisLightness * lightnessFactor

                # apply new hue and lightness to frame-buffer
                (r, g, b) = self.colorCalculator.convertHslToRgb(
                    targetHue, self.colors.basisSaturation, targetLightness)
                self.device.setRgbColorToBufferForLedWithCoordinates(
                    r, g, b, x, y)

    # ***** getter **********************************

    def getColorForCoordinates(self, x, y):
        intensity = math.sin(
            self.sinSummands[x][y] - (self.iterationStep * self.speed))

        newHue = intensity * self.degreeFactor
        newLightness = (intensity * 0.5) + 0.5
        return (newHue, newLightness)

    def getAttributes(self):
        return {
            'size': self.distanceToDarkness,
            'speed': self.speed,
            'oscillation': self.degreeOfColorDivergence,
            'posX': self.centerPositionX,
            'posY': self.centerPositionY
        }

    # ***** setter **********************************

    def setAttributes(self, attributes):
        recalculationRequired = False

        if self.isset(attributes, 'size'):
            size = self.saveFloatConvert(attributes['size'])
            if size > 0:
                self.distanceToDarkness = size
                recalculationRequired = True
        if self.isset(attributes, 'speed'):
            speed = self.saveFloatConvert(attributes['speed'])
            if speed >= 0:
                self.speed = speed
        if self.isset(attributes, 'oscillation'):
            oscillation = self.saveIntConvert(attributes['oscillation'])
            if oscillation >= 0 and oscillation <= 360:
                self.degreeOfColorDivergence = oscillation
                recalculationRequired = True
        if self.isset(attributes, 'posX'):
            posX = self.saveFloatConvert(attributes['posX'])
            if posX >= 0 and posX <= 6:
                self.centerPositionX = posX
                recalculationRequired = True
        if self.isset(attributes, 'posY'):
            posY = self.saveFloatConvert(attributes['posY'])
            if posY >= 0 and posY <= 6:
                self.centerPositionY = posY
                recalculationRequired = True

        if recalculationRequired:
            self.start()
