#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# definde import paths
import sys
sys.path.append('animations')

# import python libs
import argparse
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

# defining constants
BE_VERBOSE = False
SHOW_UPDATE_RATE = False
ANTWORTEN_GREEN = 0x86BC25
FACEBOOK_BLUE = 0x558FC6
ORANGE = 0xff4200
WHITE = 0xffffff



class LightAnimation:
    def __init__(self): 
        # initializations
        self.device = DeviceController(BE_VERBOSE, SHOW_UPDATE_RATE)
        self.colorCalculator = ColorCalculator()
        self.basisColor = ORANGE
        self.binaryClockColor = WHITE

        # initialize animations
        self.randomGlowAnimation = RandomGlowAnimation(self)
        self.pulsingCircleAnimation = PulsingCircleAnimation(self)
        self.binaryClockAnimation = BinaryClockAnimation(self, BE_VERBOSE)

        # set animation mode
        self.showRandomGlow = False
        self.showPulsingCircle = True
        self.showBinaryClock = False

        # start timers of the selected animations
        self.prepareAnimations()

        # define helper for calculation time tracking
        currentTime = lambda: int(round(time.time() * 1000))

        # run light animations
        try:
            while True:
                # measure current time
                animationStartTime = datetime.datetime.now()

                # modify frame buffer with animation
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
            self.binaryClockAnimation.start()
        else:
            self.binaryClockAnimation.stop()

    def getDevice(self):
        return self.device

    def getBasisColor(self):
        return self.basisColor

    def getBinaryClockColor(self):
        return self.binaryClockColor



# ************************************************
# non object orientated entry code goes down here:
# ************************************************

# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Controller program for Arduino powerd RGB-LED strand")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", help = "enables verbose mode")
    parser.add_argument("-fps", "--updates", action = "store_true", dest = "updates", help = "display USB update rate per second")
    args = parser.parse_args()

    if args.verbose:
        BE_VERBOSE = True

    if args.updates:
        SHOW_UPDATE_RATE = True

    lightAnimation = LightAnimation()
