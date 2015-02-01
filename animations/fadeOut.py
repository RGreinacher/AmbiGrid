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
        currentLightness = self.animationController.basisLightness

        if currentLightness > 0:
            timeDelta =  datetime.datetime.now() - self.startTime
            timeToDarkness =  self.secondsToFadeOut - timeDelta.seconds

            if timeToDarkness > 0:
                framesToDarkness = self.device.getCurrentFps() * timeToDarkness
                lightnessDeltaPerFrame = currentLightness / framesToDarkness
            else:
                lightnessDeltaPerFrame = 1 / self.device.getCurrentFps()

            self.animationController.setBasisLightness(currentLightness - lightnessDeltaPerFrame)
        else:
            self.animationController.setBasisLightness(0)
            self.animationController.stopAnimation(self)



        # if framesToDarkness > 0:
        #     lightnessDeltaPerFrame = self.animationController.basisLightness / framesToDarkness
        #     self.animationController.setBasisLightness(self.animationController.basisLightness - lightnessDeltaPerFrame)
        # else:
        #     self.animationController.setBasisLightness(0)
        #     self.animationController.stopAnimation(self)
