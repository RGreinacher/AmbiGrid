#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# This entry point to the project handles command line arguments and starts
# the application with all its components.

# definde import paths
import sys
sys.path.append('system')

# import python libs
from daemonize import Daemonize
import argparse

# import project libs
from animationController import LightAnimation
from networkInterface import AmbiGridNetworking
from webappServer import AmbiGridHttpServer

# defining variable
beVerbose = False
showFPS = False
useWebSocketsApi = True
webSocketsPort = 4445
startHttpServerForWebapp = True



def startAnimationControllerThread():
    if startHttpServerForWebapp:
        httpServer = AmbiGridHttpServer(webSocketsPort, beVerbose)
        httpServer.start()
    
    lightAnimation = LightAnimation(beVerbose, showFPS)
    lightAnimation.start()



    if useWebSocketsApi:
        AmbiGridNetworking(webSocketsPort, lightAnimation, beVerbose)

# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Controller program for Arduino powerd RGB-LED strand")
    parser.add_argument(
        "--no-api",
        action="store_true",
        dest="websockets",
        help="doesn't start the web socket API")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="set the network port number")
    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        dest="daemon",
        help="enables daemon mode")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="enables verbose mode")
    parser.add_argument(
        "-fps",
        "--updates",
        action="store_true",
        dest="updates", help="display USB update rate per second")
    parser.add_argument(
        "--no-http",
        action="store_true",
        dest="http", help="doesn't start the HTTP server for the webapp")
    args = parser.parse_args()

    if args.websockets:
        useWebSocketsApi = False

    if args.port:
        webSocketsPort = args.port

    if args.verbose:
        beVerbose = True

    if args.updates:
        showFPS = True

    if args.http:
        startHttpServerForWebapp = False

    if args.daemon:
        pidFile = "/tmp/sleepServerDaemon.pid"
        daemon = Daemonize(
            app='SleepServer Daemon',
            pid=pidFile,
            action=startAnimationControllerThread)
        daemon.start()
    else:
        startAnimationControllerThread()
