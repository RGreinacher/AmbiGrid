#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import datetime

# import project libs
from colorController import ColorController



class FadeOutAnimation:

    def __init__(self, animationController):
        # animation settings
        self.secondsToFadeOut = -1
        self.startTime = -1
        self.currentFrameNumber = 0
        self.lastAppliedLightness = 1

        # initializations
        self.animationController = animationController
        self.device = self.animationController.getDevice()
        self.colors = ColorController
        self.originalHue = 0
        self.originalSaturation = 0
        self.originalLightness = 0

    def start(self):
        self.startTime = datetime.datetime.now()
        self.currentFrameNumber = 0
        self.lastAppliedLightness = 1
        self.originalHue = self.colors.basisHue
        self.originalSaturation = self.colors.basisSaturation
        self.originalLightness = self.colors.basisLightness

    def renderNextFrame(self):
        self.currentFrameNumber = self.currentFrameNumber + 1
        totalFramesCount = self.secondsToFadeOut * self.device.getCurrentFps()

        if self.currentFrameNumber < totalFramesCount:
            targetLightness = self.quadraticalLightnessDecrease(
                totalFramesCount, self.currentFrameNumber)
            if targetLightness < self.lastAppliedLightness:
                self.colors.setBasisLightness(targetLightness)
                self.lastAppliedLightness = targetLightness
        else:
            self.colors.setBasisLightness(0)
            self.animationController.stopAnimation(self)

    def linearLightnessDecrease(self, totalFramesCount, currentFrameNumber):
        return self.originalLightness - ((currentFrameNumber / totalFramesCount) * self.originalLightness)

    def quadraticalLightnessDecrease(self, totalFramesCount, currentFrameNumber):
        squarePart = ((currentFrameNumber / totalFramesCount) - 1)
        return squarePart * squarePart * self.originalLightness

    def getSecondsToFadeOut(self):
        if self.startTime == -1 or not self.animationController.showFadeOut:
            return -1

        timeSinceStart = datetime.datetime.now() - self.startTime
        return self.secondsToFadeOut - timeSinceStart.seconds
