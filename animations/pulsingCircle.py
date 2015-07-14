#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
from array import array
import math

# defining constants
MAX_INT = 2147483647



class PulsingCircleAnimation:
  def __init__(self, animationController):
    # animation settings
    self.centerPositionX = 1
    self.centerPositionY = 5
    self.degreeOfColorDivergence = 30
    self.distanceToDarkness = 3
    self.speed = 100
    self.iterationStep = 0

    # initializations
    self.animationController = animationController
    self.colorCalculator = animationController.colorCalculator
    self.device = self.animationController.getDevice()

    # construct array of precalculated values
    self.sinSummands = [
      [
        0.0 for x in range(self.device.getNumberOfLeds())
      ] for x in range(self.device.getNumberOfLeds())
    ]

  def start(self):
    # precalculated values
    self.speedFactor = 1 / self.speed
    self.degreeFactor = ((self.degreeOfColorDivergence / 360) / 2)

    # calculate values for each pixel position
    for i in range(0, self.device.getNumberOfLeds()):
      for j in range(0, self.device.getNumberOfLeds()):
        x = i - self.centerPositionX
        y = j - self.centerPositionY
        self.sinSummands[i][j] = (math.sqrt((x * x) + (y * y)) * math.pi) / self.distanceToDarkness

  def renderNextFrame(self):
    # handle iteration counting and limit it to maxint
    if self.iterationStep < MAX_INT:
      self.iterationStep = self.iterationStep + 1
    else:
      self.iterationStep = 0

    for x in range(0, 7):
      for y in range(0, 7):
        # calculate new hue and lightness for current frame
        (hueAddition, lightnessFactor) = self.getColorForCoordinates(x, y)
        targetHue = self.animationController.basisHue + hueAddition
        targetLightness = self.animationController.basisLightness * lightnessFactor

        # apply new hue and lightness to frame-buffer
        (r, g, b) = self.colorCalculator.convertHslToRgb(targetHue, self.animationController.basisSaturation, targetLightness)
        self.device.setRgbColorToBufferForLedWithCoordinates(r, g, b, x, y)

  def getColorForCoordinates(self, x, y):
    intensity = math.sin(self.sinSummands[x][y] - (self.iterationStep * self.speedFactor))

    newHue = intensity * self.degreeFactor
    newLightness = (intensity * 0.5) + 0.5
    return (newHue, newLightness)

