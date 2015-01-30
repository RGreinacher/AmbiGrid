#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import datetime



class FadeOutAnimation:
    def __init__(self, animationController):
        # animation settings
        self.secondsToFadeOut = -1
        self.startTime = -1

        # initializations
        self.animationController = animationController
        self.device = self.animationController.getDevice()
        self.colorCalculator = animationController.colorCalculator

    def start(self):
        self.startTime = datetime.datetime.now()
        self.originalHue = self.animationController.basisHue
        self.originalSaturation = self.animationController.basisSaturation

    def renderNextFrame(self):
        timeToDarkness =  datetime.datetime.now() - self.startTime
        framesToDarkness = self.device.getCurrentFps() * (self.secondsToFadeOut - timeToDarkness.seconds)

        if framesToDarkness > 0:
            lighntessDeltaPerFrame = self.animationController.basisLightness / framesToDarkness
            self.animationController.setBasisLightness(self.animationController.basisLightness - lighntessDeltaPerFrame)
        else:
            self.animationController.setBasisLightness(0)
