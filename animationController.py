#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# definde import paths
import sys
sys.path.append('animations')

# import python libs
import argparse
from daemonize import Daemonize
from threading import Thread, Event, Timer
from array import array
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

# defining constants
BE_VERBOSE = False
SHOW_UPDATE_RATE = False
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
        self.basisLightness = 0.5
        self.calculateVariationsOfBasisValues()

        # initialize animations
        self.randomGlowAnimation = RandomGlowAnimation(self)
        self.pulsingCircleAnimation = PulsingCircleAnimation(self)
        self.binaryClockAnimation = BinaryClockAnimation(self, BE_VERBOSE)
        self.monoColor = MonoColor(self)

        # set animation mode
        self.showMonoColor = True
        self.showRandomGlow = False
        self.showPulsingCircle = False
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
                if self.showMonoColor:
                    self.monoColor.renderNextFrame()
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
        # perpare pulsing circle
        if self.showPulsingCircle:
            self.pulsingCircleAnimation.start()

        # prepare binary clock buffer
        if self.showBinaryClock:
            self.binaryClockAnimation.start(self.showRandomGlow or self.showPulsingCircle)
        else:
            self.binaryClockAnimation.stop()

    def calculateVariationsOfBasisValues(self):
        self.calculateBasisColorValues()
        self.calculateBinaryClockRgbValues()

    def calculateBasisColorValues(self):
        (bHue, bSaturation, bLightness) = self.colorCalculator.convertHexColorToHSL(self.basisColor)
        (bR, bG, bB) = self.colorCalculator.convertHexColorToRgb(self.basisColor)
        self.basisHue = bHue
        self.basisSaturation = bSaturation
        self.basisRedChannel = bR
        self.basisGreenChannel = bG
        self.basisBlueChannel = bB

    def calculateBinaryClockRgbValues(self):
        (r, g, b) = self.colorCalculator.convertHexColorToRgb(self.binaryClockColor)
        self.binaryClockColorRedChannel = r
        self.binaryClockColorGreenChannel = g
        self.binaryClockColorBlueChannel = b

    # ***** getters **********************************
    def getDevice(self):
        return self.device

    def getBasisColorAsHexColor(self):
        return self.basisColor

    def getBasisColorAsRgb(self):
        return (self.basisRedChannel, self.basisGreenChannel, self.basisBlueChannel)

    def getBasisColorAsHsl(self):
        return (self.basisHue, self.basisSaturation, self.basisLightness)

    def getBinaryClockColorAsHex(self):
        return self.binaryClockColor

    def getBinaryClockColorAsRgb(self):
        return (self.binaryClockColorRedChannel, self.binaryClockColorGreenChannel, self.binaryClockColorBlueChannel)

    # ***** setters **********************************
    def setBasisColor(self, hexColor):
        self.basisColor = hexColor
        self.calculateBasisColorValues()

    def setBinaryClockColor(self, hexColor):
        self.binaryClockColor = hexColor
        self.calculateBinaryClockRgbValues()

    def setBasisLightness(self, lightness):
        self.basisLightness = lightness
        self.setBasisColor(self.colorCalculator.convertHslToHexColor(self.basisHue, self.basisSaturation, lightness))

    # possible values for animation (string):
    # 'randomGlow'
    # 'pulsingCircle'
    # 'binaryClock'
    # 'binaryClockWithPulsingCircle'
    def showAnimation(self, animation):
        if animation == 'randomGlow':
            self.showMonoColor = False
            self.showRandomGlow = True
            self.showPulsingCircle = False
            self.showBinaryClock = False
        elif animation == 'pulsingCircle':
            self.showMonoColor = False
            self.showRandomGlow = False
            self.showPulsingCircle = True
            self.showBinaryClock = False
        elif animation == 'binaryClock':
            self.showMonoColor = False
            self.showRandomGlow = False
            self.showPulsingCircle = False
            self.showBinaryClock = True
        elif animation == 'binaryClockWithPulsingCircle':
            self.showMonoColor = False
            self.showRandomGlow = False
            self.showPulsingCircle = True
            self.showBinaryClock = True
        elif animation == 'monoColor':
            self.showMonoColor = True
            self.showRandomGlow = False
            self.showPulsingCircle = False
            self.showBinaryClock = False

        self.prepareAnimations()



# ************************************************
# non object orientated entry code goes down here:
# ************************************************
def startAnimationControllerThread():
    lightAnimation = LightAnimation()
    lightAnimation.start()

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
        elif entered == 'color':
            color = input('hex color: ')
            color = int(color, 16)
            print('setBasisColor(' + str(color) + ')')
            lightAnimation.setBasisColor(color)
        elif entered == 'ccolor':
            color = input('hex color: ')
            color = int(color, 16)
            print('setBinaryClockColor(' + str(color) + ')')
            lightAnimation.setBinaryClockColor(color)
        elif entered == 'lightness':
            lightness = input('lightness [0..100]: ')
            lightness = int(lightness) / 100
            print('setBasisLightness(' + str(lightness) + ')')
            lightAnimation.setBasisLightness(lightness)
        else:
            print('unrecognized command!')

# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Controller program for Arduino powerd RGB-LED strand")
    parser.add_argument("-d", "--daemon", action = "store_true", dest = "daemon", help = "enables daemon mode")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", help = "enables verbose mode")
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
        startAnimationControllerThread()
