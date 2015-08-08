#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import math
import random

# import project libs
from colorCalculator import ColorCalculator
from colorController import ColorController
from issetHelper import IssetHelper



class RandomGlowAnimation(IssetHelper):

    def __init__(self, device):
        # animation settings
        self.glowingPixelCount = 17
        self.glowingPixelDegreeOfColorDivergence = 35
        self.minimumSpeed = 50

        # initializations
        self.colorCalculator = ColorCalculator()
        self.colors = ColorController
        self.device = device
        self.randomGlowingPixels = {}
        self.sinFactorForHueAddition = 0

    def start(self):
        # precalculate factor needed for every iteration
        self.sinFactorForHueAddition = (
            (self.glowingPixelDegreeOfColorDivergence / 360) / 2)

        # initialize glowing pixels list
        for i in range(0, self.glowingPixelCount):
            self.randomGlowingPixels[i] = self.initializeRandomPixel()

    def renderNextFrame(self):
        for i in range(0, self.glowingPixelCount):
            glowingPixel = self.randomGlowingPixels[i]
            glowingPixel['xAxisPosition'] = glowingPixel['xAxisPosition'] + 1

            if (glowingPixel['xAxisPosition'] / glowingPixel['speedFactor']) > (math.pi * 2):
                self.randomGlowingPixels[i] = self.initializeRandomPixel()
            else:
                # calculate new hue and lightness for current frame
                (hueAddition, lightnessFactor) = self.getColorForIteration(
                    glowingPixel['xAxisPosition'], glowingPixel['speedFactor'])
                targetHue = self.colors.basisHue + hueAddition
                targetLightness = self.colors.basisLightness * lightnessFactor

                # apply new hue and lightness to frame-buffer
                (r, g, b) = self.colorCalculator.convertHslToRgb(
                    targetHue, self.colors.basisSaturation, targetLightness)
                self.device.setRgbColorToBufferForLedWithIndex(
                    r, g, b, glowingPixel['index'])

    def getColorForIteration(self, xAxisPosition, speedFactor):
        sinus = math.sin(xAxisPosition / speedFactor)

        hueAddition = sinus * self.sinFactorForHueAddition
        # probably manipulate this value to make more beautiful light
        lightnessFactor = sinus * 0.5 + 0.5

        return (hueAddition, lightnessFactor)

    def initializeRandomPixel(self):
        randomIndex = random.randint(0, self.device.getNumberOfLeds() - 1)
        if not self.pixelIndexIsUsed(randomIndex):

            # set basis color to pixel
            # self.device.setRgbColorToBufferForLedWithIndex(self.colors.getBasisColorAsRgb(), randomIndex)

            # instantiate new pixel values for iterative color calculation
            speedFactor = random.randint(
                self.minimumSpeed, self.minimumSpeed * 6)
            return {
                'index': randomIndex,
                'xAxisPosition': 0,
                'speedFactor': speedFactor
            }
        else:
            return self.initializeRandomPixel()

    def pixelIndexIsUsed(self, index):
        if self.randomGlowingPixels == {}:
            return False

        for pixel in self.randomGlowingPixels:
            try:
                if pixel['index'] == index:
                    return True
            except (TypeError):
                return False
        return False

    # ***** getter **********************************

    def getAttributes(self):
        return {
            'pixelCount': self.glowingPixelCount,
            'speed': self.minimumSpeed,
            'oscillation': self.glowingPixelDegreeOfColorDivergence
        }

    # ***** setter **********************************

    def setAttributes(self, attributes):
        recalculationRequired = False

        if self.isset(attributes, 'pixelCount'):
            pixelCount = self.saveIntConvert(attributes['pixelCount'])
            if pixelCount > 0:
                self.glowingPixelCount = pixelCount
                recalculationRequired = True
        if self.isset(attributes, 'speed'):
            speed = self.saveIntConvert(attributes['speed'])
            if speed >= 0:
                self.minimumSpeed = speed
        if self.isset(attributes, 'oscillation'):
            oscillation = self.saveIntConvert(attributes['oscillation'])
            if oscillation >= 0 and oscillation <= 360:
                self.glowingPixelDegreeOfColorDivergence = oscillation
                recalculationRequired = True

        if recalculationRequired:
            self.start()
