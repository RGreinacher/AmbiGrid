#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import mimetypes
import socket
from os.path import basename
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# constants
WEBAPP_PATH = 'webapp'
PORT_BIND_RETRIES = 10 # exit if binding 10 different ports fails
FILENAME_TO_REPLACE = 'server-connection.js'
IP_VARIABLE = '$SERVER_IP'
PORT_VARIABLE = '$SERVER_PORT'



class HttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            filename = WEBAPP_PATH + '/index.html'
        else:
            filename = WEBAPP_PATH + self.path

        mimeType, _ = mimetypes.guess_type(filename)
        openMode = self.getOpenModeForMimeType(mimeType)

        # read the requested file
        try:
            fileHandler = open(filename, openMode)
            fileContent = fileHandler.read()
            fileHandler.close()
        except FileNotFoundError:
            self.send_response_only(404)
            return
        except (UnicodeDecodeError, IsADirectoryError):
            return

        # replace the server veriable IP
        if basename(filename) == FILENAME_TO_REPLACE:
            fileContent = fileContent.replace(IP_VARIABLE, self.serverIP)
            fileContent = fileContent.replace(PORT_VARIABLE, self.serverPort)

        # send HTTP header
        self.send_response(200)
        self.send_header('Content-type', mimeType)
        self.end_headers()

        # send the message body
        try:
            if openMode == 'rb':
                self.wfile.write(bytes(fileContent))
            else:
                self.wfile.write(bytes(fileContent, 'utf-8'))
        except BrokenPipeError:
            return

    def getOpenModeForMimeType(self, mimeType):
        # the only not 'text/_' mime type which is not a binary file is
        # 'application/javascript'
        if mimeType == None or not 'javascript' in mimeType:
            return 'rb'

        return 'r'

    def setReferences(self, serverIP, serverPort):
        self.serverIP = serverIP
        self.serverPort = serverPort



class AmbiGridHttpServer(Thread):

    def __init__(self, wsPort, verbose = False):
        # initializations
        self.verbose = verbose
        self.wsServerPort = str(wsPort)
        self.host = socket.gethostbyname(socket.gethostname())
        self.ports = [80, 8080, 8000, 4444, 4446]
        self.currentSelectedPortIndex = -1
        Thread.__init__(self)

    def run(self):
        httpServer = self.instantiateHttpServer()
        if self.verbose:
            serverAddressString = self.host + ':' + str(self.getPort())
            print('HTTP server: launched at', serverAddressString)
        httpServer.serve_forever()

    def instantiateHttpServer(self):
        self.currentSelectedPortIndex = self.currentSelectedPortIndex + 1
        self.checkPortBindingRetryCriteria()
        server_address = (self.host, self.getPort())

        try:
            httpRequestHandler = HttpRequestHandler
            httpRequestHandler.setReferences(
                HttpRequestHandler, self.host, self.wsServerPort)
            httpServer = HTTPServer(server_address, httpRequestHandler)
        except PermissionError:
            if self.verbose:
                print('HTTP server: run as root to try to use port 80')
            return self.instantiateHttpServer()
        except OSError:
            if self.verbose:
                print('HTTP server: port', self.getPort(), 'already taken...')
            return self.instantiateHttpServer()

        return httpServer

    def getPort(self):
        portCount = len(self.ports)
        if self.currentSelectedPortIndex >= portCount:
            offset = self.currentSelectedPortIndex + 1 - portCount
            return self.ports[portCount - 1] + offset

        return self.ports[self.currentSelectedPortIndex]

    def checkPortBindingRetryCriteria(self):
        if self.currentSelectedPortIndex == PORT_BIND_RETRIES:
            if self.verbose:
                exitingComponent = 'HTTP server: can not find '
                exitingComponent += ' an available port; exiting this component'
                print(exitingComponent)
            exit()
