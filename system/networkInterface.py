#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# Read the README.md for a basic understanding of the server API.

# import python libs
import json
import asyncio
import socket
from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.asyncio.websocket import WebSocketServerFactory

# import project libs
from issetHelper import IssetHelper
from colorController import ColorController



# This is a autobahn based web socket protocol for the AmbiGrid API.
# Read the README.md file to get an understanding of the API
class WebSocketProtocol(WebSocketServerProtocol, IssetHelper):

    def onOpen(self):
        if self.beVerbose: print('WebSocket connection open.')

    def onConnect(self, request):
        if self.beVerbose: print('\nClient connecting: {}'.format(request.peer))

    def onClose(self, wasClean, code, reason):
        if self.beVerbose: print('\nWebSocket connection closed: {}'.format(reason))

    def onMessage(self, payload, isBinary):
        if isBinary:
            return

        stringMessage = payload.decode('utf8')
        response = {}

        try:
            jsonMessage = json.loads(stringMessage)
            response = self.processRequest(jsonMessage)
        except ValueError:
            response = self.statusRequest()

        responsAsJsonString = json.dumps(response, ensure_ascii=False)
        self.sendMessage(responsAsJsonString.encode('utf8'))

    def setReferences(self, bridge, animationController, verbose):
        self.bridge = bridge
        self.animationController = animationController
        self.colors = ColorController
        self.beVerbose = verbose

    def processRequest(self, requestData):
        response = {}

        if requestData['action'] == 'setAnimation':
            self.setAnimationRequest(requestData)
        elif requestData['action'] == 'setFadeOut':
            self.setFadeOutRequest(requestData)
        elif requestData['action'] == 'stopFadeOut':
            self.stopFadeOutRequest()
        elif requestData['action'] == 'setBaseColor':
            self.setColorRequest(requestData)

        response = self.statusRequest(requestData)

        return response

    def statusRequest(self, requestData = None):
        if (self.isset(requestData, 'details') and
                requestData['details'] == True):
            return self.animationController.getStatusWithDetails()
        else:
            return self.animationController.getStatus()

    def setAnimationRequest(self, requestData):
        animationName = requestData['name']
        self.animationController.showAnimation(animationName)

    def setFadeOutRequest(self, requestData):
        time = self.saveIntConvert(requestData['seconds'])
        if time > 0:
            self.animationController.setFadeOut(time)

    def stopFadeOutRequest(self):
        self.animationController.stopFadeOut()

    def setColorRequest(self, requestData):
        colorType = requestData['type']

        if colorType == 'hex' and self.isInt(requestData['value'], 16):
            return self.colors.setBasisColorAsHex(int(requestData['value'], 16))

        elif colorType == 'rgb':
            return self.setRgbColorRequest(requestData)

        elif colorType == 'hsl':
            return self.setHslColorRequest(requestData)

    def setRgbColorRequest(self, requestData):
        try:
            redValue = int(requestData['red'])
            greenValue = int(requestData['green'])
            blueValue = int(requestData['blue'])
        except (ValueError, TypeError):
            return

        if (redValue >= 0 and redValue <= 255 and
                greenValue >= 0 and greenValue <= 255 and
                blueValue >= 0 and blueValue <= 255):
            self.colors.setBasisColorAsRgb(redValue, greenValue, blueValue)

    def setHslColorRequest(self, requestData):
        try:
            hue = float(requestData['hue'])
            saturation = float(requestData['saturation'])
            lightness = float(requestData['lightness'])
        except (ValueError, TypeError):
            return

        if (hue >= 0 and hue <= 1 and
                saturation >= 0 and saturation <= 1 and
                lightness >= 0 and lightness <= 1):
            self.colors.setBasisColorAsHsl(hue, saturation, lightness)



class AmbiGridNetworking():

    def __init__(self, wsPort, lightAnimationController, verbose = False):
        # initializations
        self.port = wsPort
        self.animationController = lightAnimationController
        self.beVerbose = verbose

        # prepare the web socket protocol
        webSocketProtocol = WebSocketProtocol
        webSocketProtocol.setReferences(
            webSocketProtocol, self, self.animationController, self.beVerbose)

        # prepare the web sockets
        factory = WebSocketServerFactory()
        factory.protocol = webSocketProtocol

        # start the server event loop
        host = socket.gethostbyname(socket.gethostname())
        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, host, self.port)
        wsServer = loop.run_until_complete(coro)

        try:
            if self.beVerbose:
                serverAddressString = host + ':' + str(self.port)
                print('WS sever: launched at', serverAddressString)
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            wsServer.close()
            loop.close()
