#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-


class MonoColor:
  def __init__(self, animationController):
    # initializations
    self.animationController = animationController
    self.colorCalculator = animationController.colorCalculator
    self.device = self.animationController.getDevice()

  def renderNextFrame(self):
    (r, g, b) = self.animationController.getBasisColorAsRgb()
    self.device.setRgbToBuffer(r, g, b)
