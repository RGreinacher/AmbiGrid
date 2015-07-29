#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

# This entry point to the project handles command line arguments and starts
# the application with all its components.

# import python libs
from daemonize import Daemonize
import argparse

# import project libs
from animationController import LightAnimation
from httpInterface import AmbiGridHttpBridge

# defining variable
be_verbose = False
show_update_rate = True
use_http_api = False
net_port = 4444



def startAnimationControllerThread():
    lightAnimation = LightAnimation()
    lightAnimation.start()

    if use_http_api:
        AmbiGridHttpBridge(net_port, lightAnimation)


# check if this code is run as a module or was included into another project
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Controller program for Arduino powerd RGB-LED strand")
    parser.add_argument(
        "-api",
        "--server",
        action="store_true",
        dest="http",
        help="enables the HTTP API")
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
    args = parser.parse_args()

    if args.http:
        use_http_api = True

    if args.port:
        net_port = args.port

    if args.verbose:
        be_verbose = True

    if args.updates:
        show_update_rate = True

    if args.daemon:
        pidFile = "/tmp/sleepServerDaemon.pid"
        daemon = Daemonize(
            app='SleepServer Daemon',
            pid=pidFile,
            action=startAnimationControllerThread)
        daemon.start()
    else:
        startAnimationControllerThread()
