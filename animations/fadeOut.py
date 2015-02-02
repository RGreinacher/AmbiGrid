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
        self.lastAppliedLightness = 1

        # initializations
        self.animationController = animationController
        self.device = self.animationController.getDevice()
        self.colorCalculator = animationController.colorCalculator

    def start(self):
        self.startTime = datetime.datetime.now()
        self.currentFrameNumber = 0
        self.lastAppliedLightness = 1
        self.originalHue = self.animationController.basisHue
        self.originalSaturation = self.animationController.basisSaturation
        self.originalLightness = self.animationController.basisLightness

    def renderNextFrame(self):
        self.currentFrameNumber = self.currentFrameNumber + 1
        totalFramesCount = self.secondsToFadeOut * self.device.getCurrentFps()

        if self.currentFrameNumber < totalFramesCount:
            targetLightness = self.quadraticalLightnessDecrease(totalFramesCount, self.currentFrameNumber)
            if targetLightness < self.lastAppliedLightness:
                self.animationController.setBasisLightness(targetLightness)
                self.lastAppliedLightness = targetLightness
        else:
            self.animationController.setBasisLightness(0)
            self.animationController.stopAnimation(self)

    def linearLightnessDecrease(self, totalFramesCount, currentFrameNumber):
        return self.originalLightness - ((currentFrameNumber / totalFramesCount) * self.originalLightness)

    def quadraticalLightnessDecrease(self, totalFramesCount, currentFrameNumber):
        squarePart = ((currentFrameNumber / totalFramesCount) - 1)
        return squarePart * squarePart * self.originalLightness
