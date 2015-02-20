#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-
# Read the description.md for a basic understanding of the server API.

# import python libs
from threading import Thread, Event, Timer
from queue import Queue
from daemonize import Daemonize
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import json
import pprint

# import project libs
from animationController import LightAnimation

# defining constants and globals:
HTTP_PORT = 4444
GOOD_NIGHT_TIME_TO_START_WITH_VOLUME_DECREASE = 600 # 10 minutes
BE_VERBOSE = False
NORMAL_STATUS = 'running'
SLEEP_TIMER_STATUS = 'goingToSleep'
SILENCE_TIMER_STATUS = 'goingToSilence'
GOOD_NIGHT_TIMER_STATUS = 'goingToSleepAndSilence'



class IssetHelper:
    def isset(self, dictionary, key):
        try:
            dictionary[key]
        except (NameError, KeyError, IndexError) as e:
            return False
        else:
            return True

    def isInt(self, integerValue, base = 10):
        try:
            int(integerValue, base)
        except (ValueError, TypeError) as e:
            return False
        else:
            return True

    def isFloat(self, floatingValue):
        try:
            float(floatingValue)
        except (ValueError, TypeError) as e:
            return False
        else:
            return True

    def isValueForIndex(self, array, valueForIndex):
        try:
            array.index(valueForIndex)
        except ValueError:
            return False
        else:
            return True

    # return a positive (and > 0) integer (the one that comes next in the array) or -1
    def getIntAfterToken(self, array, token, distanceToToken = 1):
        if self.isValueForIndex(array, token):
            tokenIndex = array.index(token)
            if (self.isset(array, tokenIndex + distanceToToken) and
                self.isInt(array[array.index(token) + distanceToToken]) and
                int(array[array.index(token) + distanceToToken]) > 0):

                return int(array[array.index(token) + distanceToToken])
        return -1

    # return a positive float (the one that comes next in the array) or -1.0
    def getFloatAfterToken(self, array, token, distanceToToken = 1):
        if self.isValueForIndex(array, token) :
            tokenIndex = array.index(token)
            if (self.isset(array, tokenIndex + distanceToToken) and
                self.isFloat(array[array.index(token) + distanceToToken]) and
                float(array[array.index(token) + distanceToToken]) >= 0):

                return float(array[array.index(token) + distanceToToken])
        return -1.0

    # return a positive float (the one that comes next in the array) or -1.0
    def getStringAfterToken(self, array, token, distanceToToken = 1):
        if self.isValueForIndex(array, token):
            tokenIndex = array.index(token)
            if self.isset(array, tokenIndex + distanceToToken):
                return array[tokenIndex + distanceToToken]

        return ''



# ambiGridApi/status -> {status: ANIMATION_NAME, baseColor: #FF0099, clockColor: #00FF99, baseLightness: [0..1], clockLightness: [0..1], currentFPS: [0..100] [, fadeOutIn: [int]]]}
# ambiGridApi/setAnimation/ANIMATION_NAME -> {STATUS}
# ambiGridApi/setFadeOut/[int]] -> {STATUS}
# ambiGridApi/stopFadeOut -> {STATUS}
# ambiGridApi/setBaseColor/hex/FF0099 -> {STATUS}
# ambiGridApi/setBaseColor/rgb/[0..255]/[0..255]/[0..255] -> {STATUS}
# ambiGridApi/setBaseColor/lightness/[0..100] -> {STATUS}
# ambiGridApi/setClockColor/hex/FF0099 -> {STATUS}
# ambiGridApi/setClockColor/rgb/[0..255]/[0..255]/[0..255] -> {STATUS}
# ambiGridApi/setClockColor/lightness/[0..100] -> {STATUS}
class HTTPController(BaseHTTPRequestHandler, IssetHelper):
    def setAmbiGridHttpBridge(self, bridge):
        self.bridge = bridge

    def do_GET(self):
        self.resourceElements = self.path.split('/')
        returnDict = {}

        if 'ambiGridApi' in self.resourceElements:
            if 'status' in self.resourceElements:
                returnDict = self.statusRequest()
            elif 'setAnimation' in self.resourceElements:
                returnDict = self.setAnimationRequest()
            elif 'setFadeOut' in self.resourceElements:
                returnDict = self.setFadeOutRequest()
            elif 'stopFadeOut' in self.resourceElements:
                returnDict = self.stopFadeOutRequest()
            elif 'setBaseColor' in self.resourceElements:
                returnDict = self.setColorRequest('base')
            elif 'setClockColor' in self.resourceElements:
                returnDict = self.setColorRequest('clock')

        # error handling for all other requests:
        if returnDict == {}:
            if BE_VERBOSE: print('AmbiGrid HTTPController: request with unrecognized arguments')
            returnDict = {'error': 'wrong address, wrong parameters or no such resource'}
            self.send_response(404)

        # headers and define the response content type
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        message = json.dumps(returnDict, ensure_ascii = False)
        try:
            self.wfile.write(bytes(message, 'UTF-8'))
        except BrokenPipeError:
            if BE_VERBOSE: print('AmbiGrid HTTPController: current connection failed (broken pipe)')
        return

    def statusRequest(self):
        self.send_response(200)
        return self.bridge.ambiGridRequest({'get': 'status'})

    def setAnimationRequest(self):
        self.send_response(202)
        animationName = self.getStringAfterToken(self.resourceElements, 'setAnimation')
        return self.bridge.ambiGridRequest({'set': 'animation', 'name': animationName})

    def setFadeOutRequest(self):
        time = self.getIntAfterToken(self.resourceElements, 'setFadeOut') # identify fade out time
        if time > 0:
            self.send_response(202)
            return self.bridge.ambiGridRequest({'set': 'fadeOut', 'time': time})
        else:
            self.send_response(400)
            if BE_VERBOSE: print('AmbiGrid HTTPController: error parsing fade out time')
            return {'error': 'bad fade out value'}

    def stopFadeOutRequest(self):
        self.send_response(202)
        return self.bridge.ambiGridRequest({'unset': 'fadeOut'})

    def setColorRequest(self, colorDifference = 'base'):
        self.send_response(202)
        ucColorDifference = colorDifference.capitalize()
        valueType = self.getStringAfterToken(self.resourceElements, 'set' + ucColorDifference + 'Color')
        secondArgument = self.getStringAfterToken(self.resourceElements, 'set' + ucColorDifference + 'Color', 2)

        if valueType == 'hex' and self.isInt(secondArgument, 16):
            return self.bridge.ambiGridRequest({'set': colorDifference + 'Color', 'valueType': 'hex', 'value': secondArgument})

        elif valueType == 'rgb' and self.isInt(secondArgument):
            redValue = int(secondArgument)
            greenValue = self.getIntAfterToken(self.resourceElements, 'set' + ucColorDifference + 'Color', 3)
            blueValue = self.getIntAfterToken(self.resourceElements, 'set' + ucColorDifference + 'Color', 4)

            if (redValue >= 0 and redValue <= 255 and
                greenValue >= 0 and greenValue <= 255 and
                blueValue >= 0 and blueValue <= 255):
                return self.bridge.ambiGridRequest({'set': colorDifference + 'Color', 'valueType': 'rgb', 'redChannel': redValue, 'greenChannel': greenValue, 'blueChannel': blueValue})

        elif valueType == 'lightness':
            lightnessValue = int(secondArgument)
            if lightnessValue >= 0 and lightnessValue <= 100:
                return self.bridge.ambiGridRequest({'set': colorDifference + 'Color', 'valueType': 'lightness', 'value': secondArgument})

        self.send_response(400)
        if BE_VERBOSE: print('AmbiGrid HTTPController: error parsing ' + colorDifference + ' color value')
        return {'error': 'bad ' + colorDifference + ' color value'}



class AmbiGridHttpBridge(IssetHelper):
    def __init__(self):
        # define members:
        # self.communicationQueue = Queue()
        # self.serverEvent = Event()
        # self.ambiGridEvent = Event()

        self.ambiGridAnimationController = LightAnimation()
        self.ambiGridAnimationController.setThreadCommunicationObjects(self.ambiGridEvent, self.communicationQueue)
        self.ambiGridAnimationController.start()

        # inital method calls
        httpController = HTTPController
        httpController.setAmbiGridHttpBridge(httpController, self)

        try:
            # Create a web server and define the handler to manage the incoming request
            server = HTTPServer(('', HTTP_PORT), httpController)
            print('AmbiGrid HTTP Sever is up and running at port:', HTTP_PORT)

            # Wait forever for incoming http requests
            server.serve_forever()

        except KeyboardInterrupt:
            if BE_VERBOSE: print('AmbiGridHttpBridge: received interrupt signal; shutting down the HTTP server')
            server.socket.close()

    def ambiGridRequest(self, message):
        if 'unset' in message:
            if message['unset'] == 'fadeOut':
                self.ambiGridAnimationController.stopFadeOut()

        elif 'set' in message:
            if message['set'] == 'fadeOut':
                self.ambiGridAnimationController.setFadeOut(message['time'])

            elif message['set'] == 'animation' and 'name' in message:
                self.ambiGridAnimationController.showAnimation(message['name'])

            elif message['set'] == 'baseColor' and 'valueType' in message:
                if message['valueType'] == 'hex' and 'value' in message:
                    self.ambiGridAnimationController.setBasisColorAsHex(message['value'])

                elif message['valueType'] == 'rgb' and 'redChannel' in message and 'greenChannel' in message and 'blueChannel' in message:
                    red = message['redChannel']
                    green = message['greenChannel']
                    blue = message['blueChannel']
                    self.ambiGridAnimationController.setBasisColorAsRgb(red, green, blue)

                elif message['valueType'] == 'lightness' and 'value' in message:
                    self.ambiGridAnimationController.setBasisLightness(message['lightness'])


            elif message['set'] == 'clockColor' and 'valueType' in message:
                if message['valueType'] == 'hex' and 'value' in message:
                    self.ambiGridAnimationController.setBinaryClockColorAsHex(message['value'])

                elif message['valueType'] == 'rgb' and 'redChannel' in message and 'greenChannel' in message and 'blueChannel' in message:
                    red = message['redChannel']
                    green = message['greenChannel']
                    blue = message['blueChannel']
                    self.ambiGridAnimationController.setBinaryClockColorAsRgb(red, green, blue)

                elif message['valueType'] == 'lightness' and 'value' in message:
                    self.ambiGridAnimationController.setBinaryClockLightness(message['lightness'])

        else:
            print('AmbiGridHttpBridge: can\'t read queued values!')
            pprint.pprint(communicatedMessage)

        return self.ambiGridAnimationController.getStatus()

        # # send status request to sleep server via communication queue
        # self.communicationQueue.put(message)
        # self.serverEvent.set()

        # # wait for answer & process it
        # self.ambiGridEvent.wait()
        # self.ambiGridEvent.clear()

        # communicatedMessage = self.communicationQueue.get()
        # if self.isset(communicatedMessage, 'status') or self.isset(communicatedMessage, 'error'):
        #     return communicatedMessage
        # else:
        #     print('AmbiGridHttpBridge: can\'t read queued values!')
        #     pprint.pprint(communicatedMessage)



# ************************************************
# non object orientated entry code goes down here:
# ************************************************
def main():
    serverInstance = AmbiGridHttpBridge()
    # serverInstance.start()

# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Backend for receiving AmgiGrid control-signals.")
    parser.add_argument("-d", "--daemon", action = "store_true", dest = "daemon", help = "enables daemon mode")
    parser.add_argument("-v", "--verbose", action = "store_true", dest = "verbose", help = "enables verbose mode")
    parser.add_argument("-p", "--port", type=int, help = "specifies the networking port number")
    args = parser.parse_args()

    if args.verbose:
        BE_VERBOSE = True

    if args.port:
        HTTP_PORT = args.port

    if args.daemon:
        pidFile = "/tmp/ambiGridHttpServerDaemon.pid"
        daemon = Daemonize(app='AmbiGrid HTTP Server Daemon', pid=pidFile, action=main)
        daemon.start()
    else:
        main()
