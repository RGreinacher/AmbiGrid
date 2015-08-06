#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# import python libs
import mimetypes
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# constants
WEBAPP_PATH = 'webapp'
PORT_BIND_RETRIES = 10 # exit if binding 10 different ports fails



class HttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            filename = WEBAPP_PATH + '/index.html'
        else:
            filename = WEBAPP_PATH + self.path

        mimeType, _ = mimetypes.guess_type(filename)
        openMode = self.getOpenModeForMimeType(mimeType)

        try:
            fileHandler = open(filename, openMode)
            fileContent = fileHandler.read()
            fileHandler.close()
        except FileNotFoundError:
            self.send_response_only(404)
            return
        except (UnicodeDecodeError, IsADirectoryError):
            return

        self.send_response(200)
        self.send_header('Content-type', mimeType)
        self.end_headers()

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



class AmbiGridHttpServer(Thread):

    def __init__(self, verbose = False):
        # initializations
        self.verbose = verbose
        self.host = socket.gethostbyname(socket.gethostname())
        self.ports = [80, 8080, 8000, 4444, 4446]
        self.curretSelectedPortIndex = -1
        Thread.__init__(self)

    def run(self):
        httpServer = self.instantiateHttpServer()
        if self.verbose:
            serverAddressString = self.host + ':' + str(self.getPort())
            print('HTTP server: launched at', serverAddressString)
        httpServer.serve_forever()

    def instantiateHttpServer(self):
        self.curretSelectedPortIndex = self.curretSelectedPortIndex + 1
        self.checkPortBindingRetryCriteria()
        server_address = (self.host, self.getPort())

        try:
            httpServer = HTTPServer(server_address, HttpRequestHandler)
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
        if self.curretSelectedPortIndex >= portCount:
            offset = self.curretSelectedPortIndex + 1 - portCount
            return self.ports[portCount - 1] + offset

        return self.ports[self.curretSelectedPortIndex]

    def checkPortBindingRetryCriteria(self):
        if self.curretSelectedPortIndex == PORT_BIND_RETRIES:
            if self.verbose:
                exitingComponent = 'HTTP server: can not find '
                exitingComponent += ' an available port; exiting this component'
                print(exitingComponent)
            exit()
