#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

from ambiGridController import DeviceController, ColorCalculator
import argparse
from threading import Thread, Event, Timer
from array import array
import time
import datetime
import math
import random
import pprint

# defining constants
MAX_INT = 2147483647
BE_VERBOSE = False

ANTWORTEN_GREEN = 0x86BC25
FACEBOOK_BLUE = 0x558FC6
ORANGE = 0xff4200
DUCKDUCK_ORANGE = 0xDE5833
WHITE = 0xffffff


class LightAnimation:
    def __init__(self): 
        # initializations
        self.device = DeviceController()
        self.colorCalculator = ColorCalculator()
        self.basisColor = ORANGE
        self.binaryClockColor = FACEBOOK_BLUE
        self.iterationStep = 0

        # set animation mode
        self.showRandomGlow = True
        self.showPulsingCircle = False
        self.showBinaryClock = False

        # prepare random glow timer
        if self.showRandomGlow:
            self.prepareRandomGlow()

        # prepare binary clock buffer
        if self.showBinaryClock:
            self.prepareBinaryClock()

        currentTime = lambda: int(round(time.time() * 1000))

        # run light animations
        try:
            while True:
                # measure current time
                animationStartTime = datetime.datetime.now()

                # handle iteration counting and limit it to maxint
                if self.iterationStep < MAX_INT:
                    self.iterationStep = self.iterationStep + 1
                else:
                    self.iterationStep = 0

                # modify frame buffer with animation
                if self.showRandomGlow:
                    self.drawRandomGlowFrame()
                if self.showPulsingCircle:
                    self.drawPulsingCircleFrame()
                if self.showBinaryClock:
                    self.applyBinaryCockToDeviceBuffer()

                # measure current time again to calculate animation time
                animationEndTime = datetime.datetime.now()
                animationTimeDelta = animationEndTime - animationStartTime

                # apply buffer to AmbiGrid
                self.device.writeBuffer(animationTimeDelta.microseconds)

        except (KeyboardInterrupt) as e:
            print('\nreceived KeyboardInterrupt; closing connection');
            self.device.closeConnection()

    # ******************** animation: pulsing circle ********************
    def drawPulsingCircleFrame(self):
        for x in range(0, 5):
            for y in range(0, 5):
                brightness = self.circleIntensity(x, y, 2, 4, self.iterationStep)
                hexColor = self.colorCalculator.setBrightnessToHexColor(self.basisColor, brightness)
                self.device.setHexColorToBufferForLedWithCoordinates(hexColor, x, y)

    def circleIntensity(self, x, y, xPosition = 2, yPosition = 2, iteration = 0):
        x = x - xPosition
        y = y - yPosition
        distanceToDarkness = 3.25 # 2.8 is exact radius to corners
        speedFactor = 38
        amplitude = 0.05 # 0 .. 0.5
        wavePosition = amplitude + 0.005 # for max orientation `(1 - amplitude)`, `amplitude` for min orientation

        intermediateStep = math.sqrt((x * x) + (y * y)) / (distanceToDarkness / math.pi)
        return (math.cos(intermediateStep + (- iteration / speedFactor)) * amplitude) + wavePosition

    # ******************** animation: random glow ********************
    def prepareRandomGlow(self):
        self.glowingPixelCount = 17
        self.glowingPixelBasisLightness = 0.3
        self.glowingPixelAmplitude = 0.299 # 0 .. 0.5
        self.glowingPixelDegreeOfColorDivergence = 35

        self.randomGlowingPixels = {}

        hexColor = self.colorCalculator.setBrightnessToHexColor(self.basisColor, self.glowingPixelBasisLightness)
        (self.basisHue, self.basisSaturation, self.basisLightness) = self.colorCalculator.convertHexToHSL(hexColor)
        self.device.setHexColorToLeds(hexColor)

        # initialize glowing pixels list
        for i in range(0, self.glowingPixelCount):
            self.randomGlowingPixels[i] = self.initializeRandomGlowingPixel()

    def drawRandomGlowFrame(self):
        for i in range(0, self.glowingPixelCount):
            glowingPixel = self.randomGlowingPixels[i]

            glowingPixel['xAxisPosition'] = glowingPixel['xAxisPosition'] + 1
            if (glowingPixel['xAxisPosition'] / glowingPixel['speedFactor']) > (math.pi * 2):
                self.randomGlowingPixels[i] = self.initializeRandomGlowingPixel()
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

    def initializeRandomGlowingPixel(self):
        randomIndex = random.randint(0, self.glowingPixelCount)
        if not self.glowingPixelIndexIsUsed(randomIndex):
            return {'index': randomIndex,
                    'xAxisPosition': 0,
                    'speedFactor': random.randint(50, 300)}
        else:
            return self.initializeRandomGlowingPixel()

    def glowingPixelIndexIsUsed(self, index):
        if self.randomGlowingPixels == {}:
            return False

        for pixel in self.randomGlowingPixels:
            try:
                if pixel['index'] == index:
                    return True
            except (TypeError) as e:
                return False
        return False

    # ******************** animation: binary clock ********************
    def prepareBinaryClock(self):
        self.binaryClockBuffer = array('B')
        for i in range(0, 25):
            self.binaryClockBuffer.append(0)
        self.binaryClockTick()

    def applyBinaryCockToDeviceBuffer(self):
        for bufferIndex in range(0, 25):
            if self.binaryClockBuffer[bufferIndex] == 1:
                self.device.setHexColorToBufferForLedWithIndex(self.binaryClockColor, self.device.convertAlignedIndexToWiredIndex(bufferIndex))

    def binaryClockTick(self):
        if not self.showPulsingCircle:
            self.device.clearBuffer()

        time = time = datetime.datetime.now().time()
        time = ["{0:b}".format(time.hour), "{0:b}".format(time.minute), "{0:b}".format(time.second)]

        # reset to clock buffer
        for i in range (0, 25):
            self.binaryClockBuffer[i] = 0

        # hours in the first line
        lengthOfBitString = len(time[0])
        prefixingZeros = 5 - lengthOfBitString
        for i in range(0, lengthOfBitString):
            self.binaryClockBuffer[prefixingZeros + i] = int(time[0][i])

        # minutes in the second / third row; seconds in the fourth / fifth row
        for timeElement in range(1, 3):
            lengthOfBitString = len(time[timeElement])
            prefixingZeros = 6 - lengthOfBitString

            for i in range(0, lengthOfBitString):
                if prefixingZeros == 0 and i == 0:
                    bufferPosition = i
                elif prefixingZeros == 0 and i > 0: # break line after the first of the six digits
                    bufferPosition = i + 4
                else:
                    bufferPosition = i + 4 + prefixingZeros

                self.binaryClockBuffer[((timeElement - 1) * 10) + 5 + bufferPosition] = int(time[timeElement][i])

        # restart timer
        self.binaryClockTimer = Timer(1, self.binaryClockTick)
        self.binaryClockTimer.start()



# ************************************************
# non object orientated entry code goes down here:
# ************************************************

# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Controller program for Arduino powerd RGB-LED strand")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", help = "enables verbose mode")
    args = parser.parse_args()

    if args.verbose:
        BE_VERBOSE = True

    lightAnimation = LightAnimation()
