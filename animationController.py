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
from monoColor import MonoColor
from monoPixel import MonoPixel
from colorChange import ColorChange
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
        self.sentAutoUpdates = 0

        # initialize animations
        self.fadeOutAnimation = FadeOutAnimation(self)
        self.monoColorAnimation = MonoColor(self.device)
        self.monoPixelAnimation = MonoPixel(self.device)
        self.colorChangeAnimation = ColorChange(self.device)
        self.randomGlowAnimation = RandomGlowAnimation(self.device)
        self.pulsingCircleAnimation = PulsingCircleAnimation(self.device)

        # set animation mode
        self.showFadeOut = False
        self.showMonoColor = False
        self.showMonoPixel = False
        self.showColorChange = False
        self.showRandomGlow = False
        self.showPulsingCircle = False

        # start the pulsing circle animation
        self.showAnimation({'name': 'colorChange'})

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
                    self.monoColorAnimation.renderNextFrame()
                if self.showMonoPixel:
                    self.monoPixelAnimation.renderNextFrame()
                if self.showColorChange:
                    self.colorChangeAnimation.renderNextFrame()
                if self.showRandomGlow:
                    self.randomGlowAnimation.renderNextFrame()
                if self.showPulsingCircle:
                    self.pulsingCircleAnimation.renderNextFrame()

                # apply buffer to AmbiGrid
                self.device.writeBuffer()

                # update status at connected clients
                self.autoUpdateStatusDetails()

        except (KeyboardInterrupt):
            print('\nreceived KeyboardInterrupt; closing connection')
            self.device.closeConnection()

    def prepareAnimations(self):
        # prepare color change
        if self.showColorChange:
            self.colorChangeAnimation.start()

        # prepare random glow
        if self.showRandomGlow:
            self.randomGlowAnimation.start()

        # perpare pulsing circle
        if self.showPulsingCircle:
            self.pulsingCircleAnimation.start()

    def stopAnimation(self, animationObj):
        # stop showing fadeOut-animation
        if isinstance(animationObj, FadeOutAnimation):
            self.showFadeOut = False

    def autoUpdateStatusDetails(self):
        if self.autoStatusCounter < self.autoUpdateTreshold:
            self.autoStatusCounter = self.autoStatusCounter + 1
            return

        self.autoStatusCounter = 0
        framesPerUpdate = self.device.getCurrentFps() / AUTO_STATUS_UPDATE_RATE
        self.autoUpdateTreshold = int(framesPerUpdate)

        if len(self.webSocketHandler) > 0:
            if self.sentAutoUpdates >= AUTO_STATUS_UPDATE_RATE:
                self.sentAutoUpdates = 0
                currentStatus = self.getAllStati()
            else:
                self.sentAutoUpdates = self.sentAutoUpdates + 1
                currentStatus = self.getStatusDetails()

            for wsHandler in self.webSocketHandler:
                wsHandler.sendDictionary(currentStatus)

    # ***** animation control **********************************
    def stopFadeOut(self):
        self.showFadeOut = False
        return self.getStatus()

    # ***** getter **********************************
    def getDevice(self):
        return self.device

    def getStatus(self):
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
            'baseColorLightness': lightness,
            'update': 'status'
        }

        secondsToFadeOut = self.fadeOutAnimation.getSecondsToFadeOut()
        if secondsToFadeOut >= 0:
            statusDictionary['fadeOutIn'] = secondsToFadeOut

        return statusDictionary

    def getAllStati(self):
        statusDictionary = self.getStatus()
        statusDictionary.update(self.getStatusDetails())
        statusDictionary['animations'] = {
            'colorChange': self.colorChangeAnimation.getAttributes(),
            'pulsingCircle': self.pulsingCircleAnimation.getAttributes(),
            'randomGlow': self.randomGlowAnimation.getAttributes()
        }
        statusDictionary['update'] = 'all'

        return statusDictionary

    def getStatusDetails(self):
        statusDictionary = {
            'currentLightness': self.colors.getTotalLightness(),
            'currentFPS': self.device.getCurrentFps(),
            'update': 'details'
        }

        secondsToFadeOut = self.fadeOutAnimation.getSecondsToFadeOut()
        if secondsToFadeOut >= 0:
            statusDictionary['fadeOutIn'] = secondsToFadeOut

        return statusDictionary

    # ***** setters **********************************
    def setFadeOut(self, seconds = 10):
        self.fadeOutAnimation.secondsToFadeOut = seconds
        self.showFadeOut = True
        self.fadeOutAnimation.start()

    def setWebSocketHandler(self, wsHandler):
        self.webSocketHandler.append(wsHandler)

    def unsetWebSocketHandler(self, wsHandler):
        try:
            self.webSocketHandler.remove(wsHandler)
        except ValueError:
            if self.verbose:
                print('failed to unset web socket handler; not registered')

    def unsetAnimation(self):
        self.showMonoColor = False
        self.showColorChange = False
        self.showRandomGlow = False
        self.showPulsingCircle = False
        self.showMonoPixel = False

    def showAnimation(self, attributes):
        self.unsetAnimation()

        if attributes['name'] == 'monoColor':
            self.showMonoColor = True
        elif attributes['name'] == 'monoPixel':
            self.showMonoPixel = True
        elif attributes['name'] == 'colorChange':
            self.showColorChange = True
            self.colorChangeAnimation.setAttributes(attributes)
        elif attributes['name'] == 'pulsingCircle':
            self.showPulsingCircle = True
            self.pulsingCircleAnimation.setAttributes(attributes)
        elif attributes['name'] == 'randomGlow':
            self.showRandomGlow = True
            self.randomGlowAnimation.setAttributes(attributes)

        self.prepareAnimations()
        self.currentAnimation = attributes['name']
