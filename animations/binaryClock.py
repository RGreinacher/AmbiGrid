#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
from threading import Timer
from array import array
import datetime



class BinaryClockAnimation:
  def __init__(self, animationController, beVerbose = False):
    # initializations
    self.animationController = animationController
    self.device = self.animationController.getDevice()

    self.clockIsRunning = False
    self.beVerbose = beVerbose
    self.clockIsOnlyAnimation = False

    # create clock buffer; each value represents a bit at the clock
    self.binaryClockBuffer = array('B')
    for i in range(0, 25):
      self.binaryClockBuffer.append(0)

  def start(self, otherAnimationsRunning):
    self.clockIsOnlyAnimation = not otherAnimationsRunning
    self.clockIsRunning = True
    self.binaryClockTick()

  def stop(self):
    if self.clockIsRunning:
      try:
        self.binaryClockTimer.cancel()
        self.clockIsRunning = False
      except:
        import sys
        import os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\n', exc_type, fname, exc_tb.tb_lineno, '\exception while trying to stop the clock timer')
        return False

  def renderNextFrame(self):
    for bufferIndex in range(0, 25):
      if self.binaryClockBuffer[bufferIndex] == 1:
        # overwrite pixel buffer with clock-used color
        r = self.animationController.binaryClockColorRedChannel
        g = self.animationController.binaryClockColorGreenChannel
        b = self.animationController.binaryClockColorBlueChannel
        index = self.device.pixelMap[bufferIndex]
        self.device.setRgbColorToBufferForLedWithIndex(r, g, b, index)

  def binaryClockTick(self):
    # clear the device buffer if the clock is the only animation to reset each LED after one second
    if self.clockIsOnlyAnimation:
      self.device.clearBuffer()

    time = time = datetime.datetime.now().time()
    time = ["{0:b}".format(time.hour), "{0:b}".format(time.minute), "{0:b}".format(time.second)]

    # reset to clock buffer
    for i in range (0, 25):
      self.binaryClockBuffer[i] = 0

    # hours in the first line
    lengthOfBitString = len(time[0])
    prefixingZeros = 5 - lengthOfBitString
    for i in range(0, lengthOfBitString):
      self.binaryClockBuffer[prefixingZeros + i] = int(time[0][i])

    # minutes in the second / third row; seconds in the fourth / fifth row
    for timeElement in range(1, 3):
      lengthOfBitString = len(time[timeElement])
      prefixingZeros = 6 - lengthOfBitString

      for i in range(0, lengthOfBitString):
        if prefixingZeros == 0 and i == 0:
          bufferPosition = i
        elif prefixingZeros == 0 and i > 0: # break line after the first of the six digits
          bufferPosition = i + 4
        else:
          bufferPosition = i + 4 + prefixingZeros

        self.binaryClockBuffer[((timeElement - 1) * 10) + 5 + bufferPosition] = int(time[timeElement][i])

    if self.beVerbose:
      print('\nbinary clock status:')
      for row in range(0, 5):
        bufferLine = ''
        for column in range(0, 5):
          if self.binaryClockBuffer[column + (row * 5)] == 1:
            bufferLine += 'X '
          else:
            bufferLine += '- '
        print(bufferLine)

    # restart timer
    self.binaryClockTimer = Timer(1, self.binaryClockTick)
    self.binaryClockTimer.start()
