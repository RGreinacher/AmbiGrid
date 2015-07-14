#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-


class MonoPixel:
  def __init__(self, animationController):
    # initializations
    self.animationController = animationController
    self.colorCalculator = animationController.colorCalculator
    self.device = self.animationController.getDevice()

    self.pixelIndex = 0
    self.framesUntilNextPixel = 10

    self.currentFrame = 0

  def renderNextFrame(self):
    if self.currentFrame >= self.framesUntilNextPixel:
      self.reset()

    (r, g, b) = self.animationController.getBasisColorAsRgb()
    targetIndex = self.device.convertAlignedIndexToWiredIndex(self.pixelIndex)
    self.device.setRgbColorToBufferForLedWithIndex(r, g, b, targetIndex)
    self.currentFrame = self.currentFrame + 1

  def reset(self):
    self.currentFrame = 0
    self.device.clearBuffer()

    if self.pixelIndex >= (self.device.getNumberOfLeds() - 1):
      self.pixelIndex = 0
    else:
      self.pixelIndex = self.pixelIndex + 1
