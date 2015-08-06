#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# definde import paths
import sys
sys.path.append('animations')
sys.path.append('system')

# import python libs
from threading import Thread

# import project libs
from ambiGridController import DeviceController
from colorController import ColorController

# import animations
from randomGlow import RandomGlowAnimation
from pulsingCircle import PulsingCircleAnimation
from binaryClock import BinaryClockAnimation
from monoColor import MonoColor
from monoPixel import MonoPixel
from fadeOut import FadeOutAnimation

# constants
AUTO_STATUS_UPDATE_RATE = 5 # updates per second


class LightAnimation(Thread):

    def __init__(self, beVerbose, showFPS):
        # initializations
        self.beVerbose = beVerbose
        self.device = DeviceController(beVerbose, showFPS)
        self.webSocketHandler = []
        self.colors = ColorController
        self.colors.setDeviceReference(self.device)
        self.currentAnimation = ''
        self.autoStatusCounter = 0
        self.autoUpdateTreshold = 10

        # initialize animations
        self.fadeOutAnimation = FadeOutAnimation(self)
        self.monoColor = MonoColor(self.device)
        self.monoPixel = MonoPixel(self.device)
        self.randomGlowAnimation = RandomGlowAnimation(self)
        self.pulsingCircleAnimation = PulsingCircleAnimation(self.device)
        self.binaryClockAnimation = BinaryClockAnimation(
            self.device, self.beVerbose)

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

                # apply buffer to AmbiGrid
                self.device.writeBuffer()

                # update status at connected clients
                self.autoUpdateStatusDetails()

        except (KeyboardInterrupt):
            print('\nreceived KeyboardInterrupt; closing connection')
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
            self.binaryClockAnimation.start(
                self.showRandomGlow or self.showPulsingCircle)
        else:
            self.binaryClockAnimation.stop()

    def stopAnimation(self, animationObj):
        # stop showing fadeOut-animation
        if type(animationObj) == type(self.fadeOutAnimation):
            self.showFadeOut = False

    def autoUpdateStatusDetails(self):
        if self.autoStatusCounter < self.autoUpdateTreshold:
            self.autoStatusCounter = self.autoStatusCounter + 1
            return

        self.autoStatusCounter = 0
        framesPerUpdate = self.device.getCurrentFps() / AUTO_STATUS_UPDATE_RATE
        self.autoUpdateTreshold = int(framesPerUpdate)

        if len(self.webSocketHandler) > 0:
            currentStatus = self.getStatusWithDetails()
            for wsHandler in self.webSocketHandler:
                wsHandler.sendDictionary(currentStatus)

    # ***** animation control **********************************
    def stopFadeOut(self):
        self.showFadeOut = False
        return self.getStatus()

    # ***** getters **********************************
    def getDevice(self):
        return self.device

    def getStatus(self):
        secondsToFadeOut = self.fadeOutAnimation.getSecondsToFadeOut()
        hue, saturation, lightness = self.colors.getBasisColorAsHsl()
        redChannel, greenChannel, blueChannel = self.colors.getBasisColorAsRgb()

        statusDictionary =  {
            'status': self.currentAnimation,
            'baseHexColor': self.colors.getBasisColorAsHex(),
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
        statusDictionary['currentLightness'] = self.colors.getTotalLightness()
        statusDictionary['currentFPS'] = self.device.getCurrentFps()

        return statusDictionary

    def getOnlyStatusDetails(self):
        statusDictionary = {}
        statusDictionary['currentLightness'] = self.colors.getTotalLightness()
        statusDictionary['currentFPS'] = self.device.getCurrentFps()

        return statusDictionary

    # ***** setters **********************************
    def setFadeOut(self, seconds = 10):
        self.fadeOutAnimation.secondsToFadeOut = seconds
        self.showFadeOut = True
        self.fadeOutAnimation.start()

    def setWebSocketHandler(self, wsHandler):
        self.webSocketHandler.append(wsHandler)

    def unsetWebSocketHandler(self, wsHandler):
        self.webSocketHandler.remove(wsHandler)

    def showAnimation(self, animation):
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

        (self.showMonoColor,
        self.showRandomGlow,
        self.showPulsingCircle,
        self.showBinaryClock) = setterTuple

        self.prepareAnimations()
