#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# definde import paths
import sys
sys.path.append('animations')
sys.path.append('system')

# import python libs
from daemonize import Daemonize
from threading import Thread, Event, Timer
from array import array
import argparse
import time
import datetime
import math
import pprint

# import project libs
from ambiGridController import DeviceController
from colorCalculator import ColorCalculator

#import animations
from randomGlow import RandomGlowAnimation
from pulsingCircle import PulsingCircleAnimation
from binaryClock import BinaryClockAnimation
from monoColor import MonoColor
from monoPixel import MonoPixel
from fadeOut import FadeOutAnimation

# defining constants
BE_VERBOSE = False
SHOW_UPDATE_RATE = True
ANTWORTEN_GREEN = 0x86BC25
FACEBOOK_BLUE = 0x558FC6
ORANGE = 0xff4200
WHITE = 0xffffff



class LightAnimation(Thread):
    def __init__(self):
        # initializations
        self.device = DeviceController(BE_VERBOSE, SHOW_UPDATE_RATE)
        self.colorCalculator = ColorCalculator()
        self.basisColor = ORANGE
        self.binaryClockColor = WHITE
        self.basisLightness = 0.51
        self.binaryClockLightness = 1
        self.calculateVariationsOfBasisValues()
        self.currentAnimation = ''

        # initialize animations
        self.fadeOutAnimation = FadeOutAnimation(self)
        self.monoColor = MonoColor(self)
        self.monoPixel = MonoPixel(self)
        self.randomGlowAnimation = RandomGlowAnimation(self)
        self.pulsingCircleAnimation = PulsingCircleAnimation(self)
        self.binaryClockAnimation = BinaryClockAnimation(self, BE_VERBOSE)

        # set animation mode
        self.showFadeOut = False
        self.showMonoColor = False
        self.showMonoPixel = False
        self.showRandomGlow = False
        self.showPulsingCircle = True
        self.showBinaryClock = False

        # start timers of the selected animations
        self.prepareAnimations()

        # instantiate as thread
        Thread.__init__(self)

    def run(self):
        # run light animations
        try:
            while True:
                # measure current time
                animationStartTime = datetime.datetime.now()

                # modify frame buffer with animation
                if self.showFadeOut:
                    self.fadeOutAnimation.renderNextFrame()
                if self.showMonoColor:
                    self.monoColor.renderNextFrame()
                    self.currentAnimation = 'mono color'
                if self.showMonoPixel:
                    self.monoPixel.renderNextFrame()
                    self.currentAnimation = 'mono pixel'
                if self.showRandomGlow:
                    self.randomGlowAnimation.renderNextFrame()
                    self.currentAnimation = 'random glow'
                if self.showPulsingCircle:
                    self.pulsingCircleAnimation.renderNextFrame()
                    self.currentAnimation = 'pulsing circle'
                if self.showBinaryClock:
                    self.binaryClockAnimation.renderNextFrame()
                    self.currentAnimation = 'binary clock'

                # measure current time again to calculate animation time
                animationEndTime = datetime.datetime.now()
                animationTimeDelta = animationEndTime - animationStartTime

                # apply buffer to AmbiGrid
                self.device.writeBuffer(animationTimeDelta.microseconds)

        except (KeyboardInterrupt) as e:
            print('\nreceived KeyboardInterrupt; closing connection');
            self.device.closeConnection()

    def prepareAnimations(self):
        # prepare random glow
        if self.showRandomGlow:
            self.randomGlowAnimation.start()

        # perpare pulsing circle
        if self.showPulsingCircle:
            self.pulsingCircleAnimation.start()

        # prepare binary clock buffer
        if self.showBinaryClock:
            self.binaryClockAnimation.start(self.showRandomGlow or self.showPulsingCircle)
        else:
            self.binaryClockAnimation.stop()

    def stopAnimation(self, animationObj):
        # stop showing fadeOut-animation
        if type(animationObj) == type(self.fadeOutAnimation):
            self.showFadeOut = False

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

    # ***** animation control **********************************
    def stopFadeOut(self):
        self.showFadeOut = False
        return self.getStatus()

    # ***** getters **********************************
    def getDevice(self):
        return self.device

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

    def getStatus(self):
        secondsToFadeOut = self.fadeOutAnimation.getSecondsToFadeOut()
        hue, saturation, lightness = self.getBasisColorAsHsl()
        redChannel, greenChannel, blueChannel = self.getBasisColorAsRgb()

        statusDictionary =  {
                                'status': self.currentAnimation,
                                'baseHexColor': self.getBasisColorAsHex(),
                                'baseColorRed': redChannel,
                                'baseColorGreen': greenChannel,
                                'baseColorBlue': blueChannel,
                                'baseColorHue': hue,
                                'baseColorSaturation': saturation,
                                'baseColorLightness': lightness
                            }

        if secondsToFadeOut >= 0:
            statusDictionary['fadeOutIn'] = secondsToFadeOut

        return statusDictionary

    def getStatusWithDetails(self):
        statusDictionary = self.getStatus()

        statusDictionary['currentLightness'] = self.getTotalLightness()
        statusDictionary['currentFPS'] = self.device.getCurrentFps()

        return statusDictionary

    # ***** setters **********************************
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

    def setFadeOut(self, seconds = 10):
        self.fadeOutAnimation.secondsToFadeOut = seconds
        self.showFadeOut = True
        self.fadeOutAnimation.start()

    def showAnimation(self, animation, seconds = 10):
        if animation == 'monoColor':
            setterTuple = (True, False, False, False)
        elif animation == 'randomGlow':
            setterTuple = (False, True, False, False)
        elif animation == 'pulsingCircle':
            setterTuple = (False, False, True, False)
        elif animation == 'binaryClock':
            setterTuple = (False, False, False, True)
        elif animation == 'binaryClockWithPulsingCircle':
            setterTuple = (False, False, True, True)

        (self.showMonoColor, self.showRandomGlow, self.showPulsingCircle, self.showBinaryClock) = setterTuple

        self.prepareAnimations()
