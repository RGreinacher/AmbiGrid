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
                if self.showMonoPixel:
                    self.monoPixel.renderNextFrame()
                if self.showRandomGlow:
                    self.randomGlowAnimation.renderNextFrame()
                if self.showPulsingCircle:
                    self.pulsingCircleAnimation.renderNextFrame()
                if self.showBinaryClock:
                    self.binaryClockAnimation.renderNextFrame()

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
        self.basisRedChannel = bR
        self.basisGreenChannel = bG
        self.basisBlueChannel = bB

    def calculateBasisColorValuesFomRgb(self):
        self.basisColor = self.colorCalculator.convertRgbToHexColor(self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)
        (bHue, bSaturation, bLightness) = self.colorCalculator.convertRgbToHsl(self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)
        self.basisHue = bHue
        self.basisSaturation = bSaturation

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

    def getBinaryClockColorAsHex(self):
        return self.colorCalculator.getHtmlHexStringFromRgbColor(self.binaryClockColorRedChannel, self.binaryClockColorGreenChannel, self.binaryClockColorBlueChannel)

    def getBinaryClockColorAsRgb(self):
        return (self.binaryClockColorRedChannel, self.binaryClockColorGreenChannel, self.binaryClockColorBlueChannel)

    def getBinaryClockLightness(self):
        return self.binaryClockLightness

    def getStatus(self):
        status = 'running'
        secondsToFadeOut = self.fadeOutAnimation.getSecondsToFadeOut()

        statusDictionary =  {
                                'status': status,
                                'baseColor': self.getBasisColorAsHex(),
                                'clockColor': self.getBinaryClockColorAsHex(),
                                'baseLightness': self.getBasisLightness(),
                                'clockLightness': self.getBinaryClockLightness(),
                                'currentFPS': self.device.getCurrentFps()
                            }

        if secondsToFadeOut >= 0:
            statusDictionary['fadeOutIn'] = secondsToFadeOut

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



# ************************************************
# non object orientated entry code goes down here:
# ************************************************
def startAnimationControllerThread(interactiveMode = False):
    lightAnimation = LightAnimation()
    lightAnimation.start()

    if interactiveMode:
        entered = ''
        while True:
            entered = input('call a function: ')
            if entered == 'glow':
                print('showAnimation(randomGlow)')
                lightAnimation.showAnimation('randomGlow')
            elif entered == 'circle':
                print('showAnimation(pulsingCircle)')
                lightAnimation.showAnimation('pulsingCircle')
            elif entered == 'clock':
                print('showAnimation(binaryClock)')
                lightAnimation.showAnimation('binaryClock')
            elif entered == 'cc':
                print('showAnimation(binaryClockWithPulsingCircle)')
                lightAnimation.showAnimation('binaryClockWithPulsingCircle')
            elif entered == 'mono':
                print('showAnimation(monoColor)')
                lightAnimation.showAnimation('monoColor')
            elif entered == 'fade':
                seconds = int(input('seconds to fade out: '))
                print('showAnimation(fadeOut, ' + str(seconds) + ')')
                lightAnimation.showAnimation('fadeOut', seconds)
            elif entered == 'color':
                color = input('hex color: ')
                color = int(color, 16)
                print('setBasisColorAsHex(' + str(color) + ')')
                lightAnimation.setBasisColorAsHex(color)
            elif entered == 'ccolor':
                color = input('hex color: ')
                color = int(color, 16)
                print('setBinaryClockColorAsHex(' + str(color) + ')')
                lightAnimation.setBinaryClockColorAsHex(color)
            elif entered == 'lightness':
                lightness = input('lightness [0..100]: ')
                lightness = int(lightness) / 100
                print('setBasisLightness(' + str(lightness) + ')')
                lightAnimation.setBasisLightness(lightness)
            elif entered == 'clightness':
                lightness = input('lightness [0..100]: ')
                lightness = int(lightness) / 100
                print('setBinaryClockLightness(' + str(lightness) + ')')
                lightAnimation.setBinaryClockLightness(lightness)
            else:
                print('unrecognized command!')

# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Controller program for Arduino powerd RGB-LED strand")
    parser.add_argument("-d", "--daemon", action = "store_true", dest = "daemon", help = "enables daemon mode")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", help = "enables verbose mode")
    parser.add_argument("-i", "--interactive", action = "store_true", dest = "interactive", help = "enables interactive mode")
    parser.add_argument("-fps", "--updates", action = "store_true", dest = "updates", help = "display USB update rate per second")
    args = parser.parse_args()

    if args.verbose:
        BE_VERBOSE = True

    if args.updates:
        SHOW_UPDATE_RATE = True

    if args.daemon:
        pidFile = "/tmp/sleepServerDaemon.pid"
        daemon = Daemonize(app='SleepServer Daemon', pid=pidFile, action=startAnimationControllerThread)
        daemon.start()
    else:
        startAnimationControllerThread(args.interactive and not SHOW_UPDATE_RATE)
