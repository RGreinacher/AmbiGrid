#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import math
import random



class RandomGlowAnimation:
    def __init__(self, animationController):
        # animation settings
        self.glowingPixelCount = 17
        self.glowingPixelBasisLightness = 0.3
        self.glowingPixelAmplitude = 0.299 # 0 .. 0.5
        self.glowingPixelDegreeOfColorDivergence = 35

        # initializations
        self.animationController = animationController
        self.colorCalculator = animationController.colorCalculator
        self.device = self.animationController.getDevice()
        self.randomGlowingPixels = {}

        hexColor = self.colorCalculator.setBrightnessToHexColor(self.animationController.getBasisColor(), self.glowingPixelBasisLightness)
        (self.basisHue, self.basisSaturation, self.basisLightness) = self.colorCalculator.convertHexToHSL(hexColor)
        self.device.setHexColorToLeds(hexColor)

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
                (r, g, b) = self.device.getRgbFromBufferWithIndex(glowingPixel['index'])
                (h, s, l) = self.colorCalculator.convertRgbToHsl(r, g, b)
                (hueAddition, newLightness) = self.getColorForIteration(glowingPixel['xAxisPosition'], glowingPixel['speedFactor'])
                (r, g, b) = self.colorCalculator.convertHslToRgb(self.basisHue + hueAddition, self.basisSaturation, newLightness)
                self.device.setRgbColorToBufferForLedWithIndex(r, g, b, glowingPixel['index'])

    def getColorForIteration(self, xAxisPosition, speedFactor):
        newLightness = math.sin(xAxisPosition / speedFactor) * self.glowingPixelAmplitude + self.glowingPixelBasisLightness
        newHue = math.sin(xAxisPosition / speedFactor) * ((self.glowingPixelDegreeOfColorDivergence / 360) / 2)
        return (newHue, newLightness)

    def initializeRandomPixel(self):
        randomIndex = random.randint(0, self.device.getNumberOfLeds() - 1)
        if not self.pixelIndexIsUsed(randomIndex):
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
            except (TypeError) as e:
                return False
        return False
