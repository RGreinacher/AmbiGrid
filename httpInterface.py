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
                returnDict = self.setColorRequest('base')
            elif 'setClockColor' in self.resourceElements:
                returnDict = self.setColorRequest('clock')

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

    def setColorRequest(self, colorDifference='base'):
        self.send_response(202)
        ucColorDifference = colorDifference.capitalize()
        valueType = self.getStringAfterToken(
            self.resourceElements, 'set' + ucColorDifference + 'Color')
        secondArgument = self.getStringAfterToken(
            self.resourceElements, 'set' + ucColorDifference + 'Color', 2)

        if valueType == 'hex' and self.isInt(secondArgument, 16):
            return self.bridge.ambiGridRequest({'set': colorDifference + 'Color', 'valueType': 'hex', 'value': secondArgument})

        elif valueType == 'rgb' and self.isInt(secondArgument):
            redValue = int(secondArgument)
            greenValue = self.getIntAfterToken(
                self.resourceElements, 'set' + ucColorDifference + 'Color', 3)
            blueValue = self.getIntAfterToken(
                self.resourceElements, 'set' + ucColorDifference + 'Color', 4)

            if (redValue >= 0 and redValue <= 255 and
                    greenValue >= 0 and greenValue <= 255 and
                    blueValue >= 0 and blueValue <= 255):
                return self.bridge.ambiGridRequest({'set': colorDifference + 'Color', 'valueType': 'rgb', 'redChannel': redValue, 'greenChannel': greenValue, 'blueChannel': blueValue})

        elif valueType == 'lightness' and self.isInt(secondArgument):
            lightnessValue = int(secondArgument)
            if lightnessValue >= 0 and lightnessValue <= 100:
                return self.bridge.ambiGridRequest({'set': colorDifference + 'Color', 'valueType': 'lightness', 'value': secondArgument})

        self.send_response(400)
        if self.be_verbose:
            print('AmbiGrid HTTPInterface: error parsing ' +
                  colorDifference + ' color value')
        return {'error': 'bad ' + colorDifference + ' color value'}


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
                hexValue = int(message['value'], 16)
                self.animationController.setBasisColorAsHex(
                    hexValue)

            elif message['valueType'] == 'rgb' and 'redChannel' in message and 'greenChannel' in message and 'blueChannel' in message:
                red = int(message['redChannel'])
                green = int(message['greenChannel'])
                blue = int(message['blueChannel'])
                self.animationController.setBasisColorAsRgb(
                    red, green, blue)

            elif message['valueType'] == 'lightness' and 'value' in message:
                lightness = int(message['value']) / 100
                self.animationController.setBasisLightness(
                    lightness)

    def unsetRequest(self, message):
        if message['unset'] == 'fadeOut':
            self.animationController.stopFadeOut()
