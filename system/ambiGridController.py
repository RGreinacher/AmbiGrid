#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import datetime
import serial
import sys
import os
from threading import Thread, Timer
from array import array
from time import sleep
from sys import stdout

# import project libs
from colorCalculator import ColorCalculator

# defining constants
DEVICE_FILE = '/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_741333535373514081C0-if00'
DEVICE_BAUDRATE = 115200
NUMBER_LEDS = 49
NUMBER_LED_ROWS = 7
DRY_RUN = False
DRY_RUN = True



class DeviceController:

    def __init__(self, verbose, showUpdates):
        # initializations
        self.beVerbose = verbose
        self.colorCalculator = ColorCalculator()
        self.deviceConnected = False
        self.currentFrameCount = 0
        self.targetTimePerFrame = 0.0
        self.updateFrameTimestamp = datetime.datetime.now()
        self.asyncUpdateRateController = AsyncUpdateRateController(
            self, showUpdates)
        self.pixelMap = [
            42, 43, 44, 45, 46, 47, 48, 41, 20, 21, 22, 23, 24, 25, 40, 19, 18, 17,
            16, 15, 26, 39, 10, 11, 12, 13, 14, 27, 38, 9, 8, 7, 6, 5, 28, 37, 0, 1,
            2, 3, 4, 29, 36, 35, 34, 33, 32, 31, 30
        ]

        # establish connection to device
        try:
            if not DRY_RUN:
                self.serialConnection = serial.Serial(
                    DEVICE_FILE, DEVICE_BAUDRATE)
            self.deviceConnected = True
        except serial.SerialException:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\n', exc_type, fname, exc_tb.tb_lineno,
                  '\ncan not establish a serial connection to the dev')
            exit()

        # build header for buffer
        # unsigned char array, will transfered serially to the device
        self.buffer = array('B')
        # ASCII for 'A'; magic number
        self.buffer.append(65)
        # ASCII for 'd'; magic number
        self.buffer.append(100)
        # ASCII for 'a'; magic number
        self.buffer.append(97)
        # LED count high byte
        self.buffer.append((NUMBER_LEDS - 1) >> 8)
        # LED count low byte
        self.buffer.append((NUMBER_LEDS - 1) & 0xff)
        # checksum
        self.buffer.append((NUMBER_LEDS - 1) >> 8 ^ (NUMBER_LEDS - 1) & 0xff ^ 0x55)
        for _ in range(0, (NUMBER_LEDS * 3)):
            # fill up every channel of every LED with zeros
            self.buffer.append(255)

        # calculate max. useful frame rate which the serial bus can handle
        targetFPS = (DEVICE_BAUDRATE / 8) / sys.getsizeof(self.buffer)
        self.targetTimePerFrame = 1.0 / targetFPS

        # wait for initialization
        if self.beVerbose:
            print('wait for Arduino to be initialized')
        if not DRY_RUN:
            sleep(5)
        self.asyncUpdateRateController.start()

    # ***** controller handling **********************************
    def writeBuffer(self):
        if self.deviceConnected:
            # write to serial port
            if not DRY_RUN:
                try:
                    self.serialConnection.flushOutput()
                    self.serialConnection.write(bytearray(self.buffer))
                except serial.SerialException:
                    exc_type, _, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print('\n', exc_type, fname, exc_tb.tb_lineno,
                          '\nerror sending data to device! closing connection')
                    self.closeConnection()
                    exit()

            # increment counter for FPS calculation
            self.currentFrameCount = self.currentFrameCount + 1

            # limit the frame rate to what the serial connection is capable of
            self.frameRateLimiter()

    def frameRateLimiter(self):
        # measure current time
        currentTimestamp = datetime.datetime.now()
        updateFrameTimeDelta = currentTimestamp - self.updateFrameTimestamp
        self.updateFrameTimestamp = datetime.datetime.now()
        frameCalculationTime = updateFrameTimeDelta.microseconds / 1000000

        if frameCalculationTime > self.targetTimePerFrame:
            return

        compensateTime = self.targetTimePerFrame - frameCalculationTime
        sleep(compensateTime)

    def closeConnection(self):
        self.deviceConnected = False
        if not DRY_RUN:
            self.serialConnection.close()
        if self.beVerbose:
            print('serial connection closed')

    def clearBuffer(self):
        for i in range(6, 6 + (NUMBER_LEDS * 3)):
            self.buffer[i] = 0

    # ***** getters **********************************
    def getNumberOfLeds(self):
        return NUMBER_LEDS

    def getCurrentFps(self):
        return self.asyncUpdateRateController.currentFPS

    def getRgbFromBufferWithIndex(self, index):
        bufferIndex = 6 + (index * 3)

        redChannel = self.buffer[bufferIndex]
        greenChannel = self.buffer[bufferIndex + 1]
        blueChannel = self.buffer[bufferIndex + 2]

        return (redChannel, greenChannel, blueChannel)

    def getRgbFromBufferWithCoordinates(self, xIndex, yIndex):
        return self.getRgbFromBufferWithIndex(xIndex + (yIndex * NUMBER_LED_ROWS))

    # ***** setters **********************************
    def setRgbColorToBufferForLedWithIndex(self, redChannel, greenChannel, blueChannel, ledIndex):
        ledAddress = 6 + (ledIndex * 3)
        self.buffer[ledAddress] = self.colorCalculator.frameRgbValue(
            redChannel)
        self.buffer[
            ledAddress + 1] = self.colorCalculator.frameRgbValue(greenChannel)
        self.buffer[
            ledAddress + 2] = self.colorCalculator.frameRgbValue(blueChannel)

    def setRgbColorToBufferForLedWithCoordinates(self, redChannel, greenChannel, blueChannel, xIndex, yIndex):
        alignedIndex = xIndex + (yIndex * NUMBER_LED_ROWS)
        self.setRgbColorToBufferForLedWithIndex(
            redChannel, greenChannel, blueChannel, self.pixelMap[alignedIndex]
        )

    def setRgbToBuffer(self, redChannel, greenChannel, blueChannel):
        for i in range(6, (NUMBER_LEDS * 3 + 6), 3):
            self.buffer[i] = self.colorCalculator.frameRgbValue(redChannel)
            self.buffer[
                i + 1] = self.colorCalculator.frameRgbValue(greenChannel)
            self.buffer[
                i + 2] = self.colorCalculator.frameRgbValue(blueChannel)



class AsyncUpdateRateController(Thread):

    def __init__(self, deviceController, showUpdates):
        self.device = deviceController
        self.showUpdates = showUpdates
        self.currentFPS = 0
        self.printUpdateRateTimer = None

        # inital method calls
        Thread.__init__(self)

    def run(self):
        self.__timerTickPrintUpdateRate()

    def __timerTickPrintUpdateRate(self):
        if self.device.deviceConnected:  # and self.device.printUpdateRate:
            if self.showUpdates:
                stdout.write(
                    "\r" + 'update rate: ' + str(self.device.currentFrameCount) + ' updates/sec ')
                stdout.flush()
            self.currentFPS = self.device.currentFrameCount
            self.device.currentFrameCount = 0

        # keep the timer alive
        self.printUpdateRateTimer = Timer(1, self.__timerTickPrintUpdateRate)
        self.printUpdateRateTimer.start()
