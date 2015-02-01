#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import datetime



class FadeOutAnimation:
    def __init__(self, animationController):
        # animation settings
        self.secondsToFadeOut = -1
        self.startTime = -1
        self.currentFrameNumber = 0

        # initializations
        self.animationController = animationController
        self.device = self.animationController.getDevice()
        self.colorCalculator = animationController.colorCalculator

    def start(self):
        self.startTime = datetime.datetime.now()
        self.currentFrameNumber = 0
        self.originalHue = self.animationController.basisHue
        self.originalSaturation = self.animationController.basisSaturation
        self.originalLightness = self.animationController.basisLightness

    def renderNextFrame(self):
        self.currentFrameNumber = self.currentFrameNumber + 1

        # timeElapsed =  datetime.datetime.now() - self.startTime

        # currentFrameNumber = timeElapsed.seconds * self.device.getCurrentFps()
        totalFramesCount = self.secondsToFadeOut * self.device.getCurrentFps()

        if self.currentFrameNumber < totalFramesCount:
            # targetLightness = self.linearLightnessDecrease(totalFramesCount, self.currentFrameNumber)
            targetLightness = self.quadraticalLightnessDecrease(totalFramesCount, self.currentFrameNumber)
            self.animationController.setBasisLightness(targetLightness)
        else:
            self.animationController.setBasisLightness(0)
            self.animationController.stopAnimation(self)

        # first attempt
        # currentLightness = self.animationController.basisLightness

        # if currentLightness > 0:
        #     timeDelta =  datetime.datetime.now() - self.startTime
        #     timeToDarkness =  self.secondsToFadeOut - timeDelta.seconds

        #     if timeToDarkness > 0:
        #         framesToDarkness = self.device.getCurrentFps() * timeToDarkness
        #         lightnessDeltaPerFrame = currentLightness / framesToDarkness
        #     else:
        #         lightnessDeltaPerFrame = 1 / self.device.getCurrentFps()

        #     self.animationController.setBasisLightness(currentLightness - lightnessDeltaPerFrame)
        # else:
        #     self.animationController.setBasisLightness(0)
        #     self.animationController.stopAnimation(self)

    def linearLightnessDecrease(self, totalFramesCount, currentFrameNumber):
        return self.originalLightness - ((currentFrameNumber / totalFramesCount) * self.originalLightness)

    def quadraticalLightnessDecrease(self, totalFramesCount, currentFrameNumber):
        squarePart = ((currentFrameNumber / totalFramesCount) - 1)
        return squarePart * squarePart * self.originalLightness