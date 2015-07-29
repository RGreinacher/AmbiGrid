#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-
# Read the description.md for a basic understanding of the server API.

# import python libs
# from threading import Thread, Event, Timer
# from queue import Queue
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# import project libs
from issetHelper import IssetHelper



# This HTTP server implements the AmbiGrid API.
# Read the README.md file to get an understanding of the API
class HTTPInterface(BaseHTTPRequestHandler, IssetHelper):

    def setReferences(self, animationController, verbose):
        self.animationController = animationController
        self.be_verbose = verbose

    def prepareResourceElements(self):
        self.resourceElements = []
        self.jsonpCallback = ''

        for element in self.path.split('/'):
            if 'callback' in element:
                secondArgumentPosition = element.find('&')
                self.jsonpCallback = element[10:secondArgumentPosition]
            else:
                self.resourceElements.append(element)

    def do_GET(self):
        self.prepareResourceElements()
        returnDict = {}

        if 'ambiGridApi' in self.resourceElements:
            if 'setAnimation' in self.resourceElements:
                self.setAnimationRequest()
            elif 'setFadeOut' in self.resourceElements:
                self.setFadeOutRequest()
            elif 'stopFadeOut' in self.resourceElements:
                self.stopFadeOutRequest()
            elif 'setBaseColor' in self.resourceElements:
                self.setColorRequest()

            if 'details' in self.resourceElements:
                returnDict = self.statusWithDetailsRequest()
            else:
                returnDict = self.statusRequest()

        # error handling for all other requests:
        if returnDict == {}:
            if self.be_verbose:
                print(
                    'AmbiGrid HTTPInterface: request with unrecognized arguments')
            returnDict = {
                'error': 'wrong address, wrong parameters or no such resource'}
            self.send_response(404)

        # create a message that may be encapsulated in a JSONP callback
        # function
        if self.jsonpCallback != '':
            self.send_header('Content-type', 'application/text')
            jsonMessage = json.dumps(returnDict, ensure_ascii=False)
            message = self.jsonpCallback + '(' + jsonMessage + ');'
        else:
            self.send_header('Content-type', 'application/json')
            message = json.dumps(returnDict, ensure_ascii=False)

        self.end_headers()

        try:
            self.wfile.write(bytes(message, 'UTF-8'))
        except BrokenPipeError:
            if self.be_verbose:
                print('AmbiGrid HTTPInterface:\
                    current connection failed (broken pipe)')
        return

    def statusRequest(self):
        self.send_response(200)
        return self.animationController.getStatus()

    # TODO
    def statusWithDetailsRequest(self):
        self.send_response(200)
        return self.animationController.getStatus()

    def setAnimationRequest(self):
        self.send_response(202)
        animationName = self.getStringAfterToken(
            self.resourceElements, 'setAnimation')
        self.animationController.showAnimation(animationName)

    def setFadeOutRequest(self):
        time = self.getIntAfterToken(self.resourceElements, 'setFadeOut')
        if time > 0:
            self.send_response(202)
            self.animationController.setFadeOut(time)
        else:
            self.send_response(400)
            if self.be_verbose:
                print('AmbiGrid HTTPInterface: error parsing fade out time')
            return {'error': 'bad fade out value'}

    def stopFadeOutRequest(self):
        self.send_response(202)
        self.animationController.stopFadeOut()

    def setColorRequest(self):
        self.send_response(202)
        valueType = self.getStringAfterToken(
            self.resourceElements, 'setBaseColor')
        secondArgument = self.getStringAfterToken(
            self.resourceElements, 'setBaseColor', 2)

        if valueType == 'hex' and self.isInt(secondArgument, 16):
            self.animationController.setBasisColorAsHex(secondArgument)

        elif valueType == 'rgb' and self.isInt(secondArgument):
            return self.setRgbColorRequest(secondArgument)

        elif valueType == 'hsl' and self.isFloat(secondArgument):
            return self.setHslColorRequest(secondArgument)

        elif valueType == 'lightness' and self.isInt(secondArgument):
            return self.setLightnessColorRequest(secondArgument)

        self.send_response(400)
        if self.be_verbose:
            print('AmbiGrid HTTPInterface: error parsing color value')

    def setRgbColorRequest(self, colorsEncoded):
        try:
            redValue = int(colorsEncoded)
            greenValue = self.getIntAfterToken(
                self.resourceElements, 'setBaseColor', 3)
            blueValue = self.getIntAfterToken(
                self.resourceElements, 'setBaseColor', 4)
        except (ValueError, TypeError):
            return

        if (redValue >= 0 and redValue <= 255 and
                greenValue >= 0 and greenValue <= 255 and
                blueValue >= 0 and blueValue <= 255):
            self.animationController.setBasisColorAsRgb(
                redValue, greenValue, blueValue)

    def setHslColorRequest(self, colorsEncoded):
        try:
            hue = float(colorsEncoded)
            saturation = self.getFloatAfterToken(
                self.resourceElements, 'setBaseColor', 3)
            lightness = self.getFloatAfterToken(
                self.resourceElements, 'setBaseColor', 4)
        except (ValueError, TypeError):
            return

        if (hue >= 0 and hue <= 1 and
                saturation >= 0 and saturation <= 1 and
                lightness >= 0 and lightness <= 1):
            self.animationController.setBasisColorAsHsl(
                hue, saturation, lightness)

    def setLightnessColorRequest(self, value):
        try:
            lightness = int(value)
        except (ValueError, TypeError):
            return

        if lightness >= 0 and lightness <= 100:
            self.animationController.setBasisLightness(
                lightness)



class AmbiGridHttpBridge(IssetHelper):

    def __init__(self, net_port, lightAnimationController, verbose = False):
        # inital method calls
        httpInterface = HTTPInterface
        httpInterface.setReferences(httpInterface, lightAnimationController, verbose)

        try:
            # Create a web server and define the handler to manage the incoming
            # request
            server = HTTPServer(('', net_port), httpInterface)
            print('AmbiGrid HTTP Sever is up and running at port:', net_port)

            # Wait forever for incoming http requests
            server.serve_forever()

        except KeyboardInterrupt:
            if self.be_verbose:
                print('AmbiGridHttpBridge: received interrupt signal;\
                    shutting down the HTTP server')
            server.socket.close()
