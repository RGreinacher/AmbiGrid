#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import math
import random

# import project libs
from colorCalculator import ColorCalculator
from colorController import ColorController



class RandomGlowAnimation:

    def __init__(self, device):
        # animation settings
        self.glowingPixelCount = 17
        self.glowingPixelDegreeOfColorDivergence = 35

        # initializations
        self.colorCalculator = ColorCalculator()
        self.colors = ColorController
        self.device = device
        self.randomGlowingPixels = {}
        self.sinFactorForHueAddition = 0

    def setAttributes(self, attributes): # TODO
        print('SETTING ATTRIBUTES NOT IMPLEMENTED FOR RANDOM GLOW')

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
                targetHue = self.animationController.basisHue + hueAddition
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
            return {'index': randomIndex,
                    'xAxisPosition': 0,
                    'speedFactor': random.randint(50, 300)}
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
