#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import serial
from threading import Thread, Event, Timer
from array import array
from time import sleep
from sys import stdout
import sys
import os

# import project libs
from colorCalculator import ColorCalculator

# defining constants
DEVICE_FILE = '/dev/tty.usbmodem14211'
# DEVICE_FILE = '/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_741333535373514081C0-if00'
DEVICE_BAUDRATE = 115200
NUMBER_LEDS = 25
TARGET_FPS = 90
BE_VERBOSE = True
# DRY_RUN = True
DRY_RUN = False



class DeviceController:
    def __init__(self):
        # initializations
        self.colorCalculator = ColorCalculator()
        self.deviceConnected = False
        self.countUpdatesBuffer = 0
        self.writeBufferSleepOffset = 0
        self.asyncConsoleEvent = Event()
        self.asyncConsole = AsyncConsole(self, self.asyncConsoleEvent)
        self.asyncConsole.start()

        # establish connection to device
        try:
            if not DRY_RUN: self.serialConnection = serial.Serial(DEVICE_FILE, DEVICE_BAUDRATE)
            self.deviceConnected = True
        except (SerialException, ValueError) as e:
            print('Can not establish a serial connection to the device: SerialException or ValueError!')
            exit()

        # build header for buffer
        self.buffer = array('B')                                                         # unsigned char array, will transfered serially to the device
        self.buffer.append(65)                                                           # ASCII for 'A'; magic number
        self.buffer.append(100)                                                          # ASCII for 'd'; magic number
        self.buffer.append(97)                                                           # ASCII for 'a'; magic number
        self.buffer.append((NUMBER_LEDS - 1) >> 8)                                       # LED count high byte
        self.buffer.append((NUMBER_LEDS - 1) & 0xff)                                     # LED count low byte
        self.buffer.append((NUMBER_LEDS - 1) >> 8 ^ (NUMBER_LEDS - 1) & 0xff ^ 0x55)     # Checksum
        for i in range (0, (NUMBER_LEDS * 3)):
            self.buffer.append(0)                                                        # fill up every channel of every LED with zeros

        # wait for initialization
        if BE_VERBOSE: print('wait for Arduino to be initialized')
        if not DRY_RUN: sleep(5)
        self.asyncConsoleEvent.set()

    def closeConnection(self):
        self.deviceConnected = False
        if not DRY_RUN:
            self.serialConnection.close()
        if BE_VERBOSE:
            print('serial connection closed')

    # correct wiring
    def convertAlignedIndexToWiredIndex(self, index):
        if index >= 0 and index <= 4: # 1st row
            index += 20
        elif index >= 20 and index <= 24: # 5th row
            index -= 20
        elif index == 5:
            index = 19
        elif index == 6:
            index = 18
        elif index == 7:
            index = 17
        elif index == 8:
            index = 16
        elif index == 9:
            index = 15
        elif index == 15:
            index = 9
        elif index == 16:
            index = 8
        elif index == 17:
            index = 7
        elif index == 18:
            index = 6
        elif index == 19:
            index = 5
        return index

    def clearBuffer(self):
        for i in range(6, 6 + (NUMBER_LEDS * 3)):
            self.buffer[i] = 0

    def getNumberOfLeds(self):
        return NUMBER_LEDS

    def getRgbFromBufferWithIndex(self, index):
        bufferIndex = 6 + (index * 3)

        redChannel = self.buffer[bufferIndex]
        greenChannel = self.buffer[bufferIndex + 1]
        blueChannel = self.buffer[bufferIndex + 2]

        return (redChannel, greenChannel, blueChannel)

    def setRgbColorToBufferForLedWithIndex(self, redChannel, greenChannel, blueChannel, ledIndex):
        ledAddress = 6 + (ledIndex * 3)
        self.buffer[ledAddress] = self.colorCalculator.frameRgbValue(redChannel)
        self.buffer[ledAddress + 1] = self.colorCalculator.frameRgbValue(greenChannel)
        self.buffer[ledAddress + 2] = self.colorCalculator.frameRgbValue(blueChannel)

    def setHexColorToBufferForLedWithIndex(self, hexColor, ledIndex):
        (redChannel, greenChannel, blueChannel) = self.colorCalculator.convertHexColorToRgb(hexColor)
        self.setRgbColorToBufferForLedWithIndex(redChannel, greenChannel, blueChannel, ledIndex)

    def setHexColorToBufferForLedWithCoordinates(self, hexColor, xIndex, yIndex):
        alignedIndex = xIndex + (yIndex * 5)
        index = self.convertAlignedIndexToWiredIndex(alignedIndex) # correct wiring
        self.setHexColorToBufferForLedWithIndex(hexColor, index)

    def setHexColorToBuffer(self, hexColor):
        (redChannel, greenChannel, blueChannel) = self.colorCalculator.convertHexColorToRgb(hexColor)

        for i in range(6, 81, 3):
            self.buffer[i] = self.colorCalculator.frameRgbValue(redChannel)
            self.buffer[i + 1] = self.colorCalculator.frameRgbValue(greenChannel)
            self.buffer[i + 2] = self.colorCalculator.frameRgbValue(blueChannel)

    def setHexColorToLeds(self, hexColor):
        self.setHexColorToBuffer(hexColor)
        self.writeBuffer()

    def writeBuffer(self, calculationTimeForFrame = 0):
        try:
            if self.deviceConnected:
                # write to serial port
                if not DRY_RUN:
                    self.serialConnection.flushOutput()
                    self.serialConnection.write(bytearray(self.buffer))

                # auto correct sleep time to reach target FPS
                calculatedSleepTime = (1 / TARGET_FPS) - (calculationTimeForFrame / 1000000)
                if self.asyncConsole.currentFramesPerSecond < TARGET_FPS:
                    self.writeBufferSleepOffset = self.writeBufferSleepOffset + 0.000001
                elif self.asyncConsole.currentFramesPerSecond > TARGET_FPS:
                    self.writeBufferSleepOffset = self.writeBufferSleepOffset - 0.000001

                if calculatedSleepTime > self.writeBufferSleepOffset:
                    sleep(calculatedSleepTime - self.writeBufferSleepOffset)
                else:
                    self.writeBufferSleepOffset = 0
                    if calculatedSleepTime > 0:
                        sleep(calculatedSleepTime)

                # increment counter for FPS calculation
                self.countUpdatesBuffer = self.countUpdatesBuffer + 1
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\n', exc_type, fname, exc_tb.tb_lineno, '\nerror sending data to device! closing connection')
            print('error values - calculationTimeForFrame: ' + str(calculationTimeForFrame) + ', writeBufferSleepOffset: ' + str(self.writeBufferSleepOffset))
            self.closeConnection()
            exit()


class AsyncConsole(Thread):
    def __init__(self, deviceController, event):
        self.device = deviceController
        self.threadingEvent = event
        self.currentFramesPerSecond = 3000

        # inital method calls
        Thread.__init__(self)

    def run(self):
        while self.threadingEvent.wait():
            self.threadingEvent.clear()
            self.__timerTickPrintUpdateRate()

    def __timerTickPrintUpdateRate(self):
        if self.device.deviceConnected: # and self.device.printUpdateRate:
            if BE_VERBOSE: stdout.write("\r" + 'update rate: ' + str(self.device.countUpdatesBuffer) + ' updates/sec ')
            stdout.flush()
            self.currentFramesPerSecond = self.device.countUpdatesBuffer
            self.device.countUpdatesBuffer = 0

        # keep the timer alive and able to cancel
        self.printUpdateRateTimer = Timer(1, self.__timerTickPrintUpdateRate)
        self.printUpdateRateTimer.start()
