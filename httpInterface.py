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

    def setReferences(self, bridge, verbose):
        self.bridge = bridge
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
            if 'status' in self.resourceElements:
                returnDict = self.statusRequest()
            elif 'setAnimation' in self.resourceElements:
                returnDict = self.setAnimationRequest()
            elif 'setFadeOut' in self.resourceElements:
                returnDict = self.setFadeOutRequest()
            elif 'stopFadeOut' in self.resourceElements:
                returnDict = self.stopFadeOutRequest()
            elif 'setBaseColor' in self.resourceElements:
                returnDict = self.setColorRequest()

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
                print(
                    'AmbiGrid HTTPInterface: current connection failed (broken pipe)')
        return

    def statusRequest(self):
        self.send_response(200)
        return self.bridge.ambiGridRequest({'get': 'status'})

    def setAnimationRequest(self):
        self.send_response(202)
        animationName = self.getStringAfterToken(
            self.resourceElements, 'setAnimation')
        return self.bridge.ambiGridRequest({'set': 'animation', 'name': animationName})

    def setFadeOutRequest(self):
        # identify fade out time
        time = self.getIntAfterToken(self.resourceElements, 'setFadeOut')
        if time > 0:
            self.send_response(202)
            return self.bridge.ambiGridRequest({'set': 'fadeOut', 'time': time})
        else:
            self.send_response(400)
            if self.be_verbose:
                print('AmbiGrid HTTPInterface: error parsing fade out time')
            return {'error': 'bad fade out value'}

    def stopFadeOutRequest(self):
        self.send_response(202)
        return self.bridge.ambiGridRequest({'unset': 'fadeOut'})

    def setColorRequest(self):
        self.send_response(202)
        valueType = self.getStringAfterToken(
            self.resourceElements, 'setBaseColor')
        secondArgument = self.getStringAfterToken(
            self.resourceElements, 'setBaseColor', 2)

        if valueType == 'hex' and self.isInt(secondArgument, 16):
            return self.setHexColorRequest(secondArgument)

        elif valueType == 'rgb' and self.isInt(secondArgument):
            return self.setRgbColorRequest(secondArgument)

        elif valueType == 'hsl' and self.isFloat(secondArgument):
            return self.setHslColorRequest(secondArgument)

        elif valueType == 'lightness' and self.isInt(secondArgument):
            return self.setLightnessColorRequest(secondArgument)

        self.send_response(400)
        if self.be_verbose:
            print('AmbiGrid HTTPInterface: error parsing color value')
        return {'error': 'bad color value'}

    def setHexColorRequest(self, value):
        return self.bridge.ambiGridRequest({
            'set': 'baseColor',
            'valueType': 'hex',
            'value': value})

    def setRgbColorRequest(self, colorsEncoded):
        redValue = int(colorsEncoded)
        greenValue = self.getIntAfterToken(
            self.resourceElements, 'setBaseColor', 3)
        blueValue = self.getIntAfterToken(
            self.resourceElements, 'setBaseColor', 4)

        if (redValue >= 0 and redValue <= 255 and
                greenValue >= 0 and greenValue <= 255 and
                blueValue >= 0 and blueValue <= 255):
            return self.bridge.ambiGridRequest({
                'set': 'baseColor',
                'valueType': 'rgb',
                'redChannel': redValue,
                'greenChannel': greenValue,
                'blueChannel': blueValue})

    def setHslColorRequest(self, colorsEncoded):
        hue = float(colorsEncoded)
        saturation = self.getFloatAfterToken(
            self.resourceElements, 'setBaseColor', 3)
        lightness = self.getFloatAfterToken(
            self.resourceElements, 'setBaseColor', 4)

        if (hue >= 0 and hue <= 1 and
                saturation >= 0 and saturation <= 1 and
                lightness >= 0 and lightness <= 1):
            return self.bridge.ambiGridRequest({
                'set': 'baseColor',
                'valueType': 'hsl',
                'hue': hue,
                'saturation': saturation,
                'lightness': lightness})

    def setLightnessColorRequest(self, value):
        lightnessValue = int(value)
        if lightnessValue >= 0 and lightnessValue <= 100:
            return self.bridge.ambiGridRequest({
                'set': 'baseColor',
                'valueType': 'lightness',
                'value': value})

class AmbiGridHttpBridge(IssetHelper):

    def __init__(self, net_port, lightAnimationController, verbose = False):
        # define members:
        # self.communicationQueue = Queue()
        # self.serverEvent = Event()
        # self.ambiGridEvent = Event()
        self.be_verbose = verbose

        self.animationController = lightAnimationController
        # self.animationController.setThreadCommunicationObjects(self.ambiGridEvent, self.communicationQueue)

        # inital method calls
        httpInterface = HTTPInterface
        httpInterface.setReferences(httpInterface, self, verbose)

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

    def ambiGridRequest(self, message):
        if 'set' in message:
            self.setRequest(message)

        elif 'unset' in message:
            self.unsetRequest(message)

        return self.animationController.getStatus()

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

    def setRequest(self, message):
        if message['set'] == 'fadeOut':
            self.animationController.setFadeOut(message['time'])

        elif message['set'] == 'animation' and 'name' in message:
            self.animationController.showAnimation(message['name'])

        elif message['set'] == 'baseColor' and 'valueType' in message:
            if message['valueType'] == 'hex' and 'value' in message:
                try:
                    hexValue = int(message['value'], 16)
                except (ValueError, TypeError):
                    return

                self.animationController.setBasisColorAsHex(
                    hexValue)

            elif (message['valueType'] == 'rgb' and
                    'redChannel' in message and
                    'greenChannel' in message and
                    'blueChannel' in message):
                try:
                    red = int(message['redChannel'])
                    green = int(message['greenChannel'])
                    blue = int(message['blueChannel'])
                except (ValueError, TypeError):
                    return

                self.animationController.setBasisColorAsRgb(
                    red, green, blue)

            elif (message['valueType'] == 'hsl' and
                    'hue' in message and
                    'saturation' in message and
                    'lightness' in message):
                try:
                    hue = float(message['hue'])
                    saturation = float(message['saturation'])
                    lightness = float(message['lightness'])
                except (ValueError, TypeError):
                    return

                self.animationController.setBasisColorAsHsl(
                    hue, saturation, lightness)

            elif message['valueType'] == 'lightness' and 'value' in message:
                lightness = int(message['value']) / 100
                self.animationController.setBasisLightness(
                    lightness)

    def unsetRequest(self, message):
        if message['unset'] == 'fadeOut':
            self.animationController.stopFadeOut()
