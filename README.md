# The AmbiGrid

Python3 framework for an Arduino controlled, programmable RGB LED mood light with a web socket interface.

## The quick look - why, how & what:

I made this YouTube video for you to get an idea of what this source code can do.

[YouTube video](http://www.youtube.com)

Basically it provides a Web Socket interface and different animations for a RGB LED matrix which is connected to the server running this software via USB (in my setup this is a Raspberry PI 2 connected to a Adruino which controlls the LEDs).

## Get it running

Clone this repo:

	git clone https://github.com/RGreinacher/AmbiGrid.git

Install [Python 3.5](https://www.python.org/downloads/) or greater.

Then you only need the following three free and open source packages: [Daemonize](https://github.com/thesharp/daemonize), [pySerial](https://github.com/pyserial/pyserial) & [Autobahn](http://autobahn.ws/python/installation.html). Install them with the following command:

	pip3 install daemonize pyserial autobahn
	
That's it. You should now be able to lauch the AmbiGrid framework:

	python3 ambiGrid.py
	
The following options will give you some control of the software:

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --verbose         enables verbose mode
	  -d, --daemon          enables daemon mode
	  -fps, --updates       display USB update rate per second
	  -p PORT, --port PORT  set the network port number
	  --no-api              doesn't start the web socket API
	  --no-http             doesn't start the HTTP server for the webapp
	  
**Pro tipp**: Run the software as root to make use of the privileged *HTTP port 80* (otherwise the HTTP web server will listen to port 8080, 8000, ... what ever is available). So my prefered command to run the software is:

	sudo python3 ambiGrid.py -v -fps
	
After you launched it the web app will be available at [http://127.0.0.1:80](http://127.0.0.1:80) (change the port number accordingly; if you don't know which port is used try the `-v` option)
	
## I just want to play around and don't have a LED matrix

Easy: You can run this software nevertheless! Just launch it as described; the web server will serve the web app, which connects via web sockets to the color calulation module and so on. What you can do with it? Play with colors! Srsly, it's fun to see what happens to the RGB values if you turn down the saturation for example. Go ahead! ;o)

## API usage:

The web socket API uses JSON to apply changes or for getting status updates. The easiest way to get an understanding of what's happening is to read the `networkInterface.py` file.

If you want me to write all the options and different requests down into this readme, just formulate an issue. :)



# Apart of the code

## Contribution & Contributors

I'd love to see your ideas for improving this project!
The best way to contribute is by submitting a pull request or a [new Github issue](https://github.com/RGreinacher/AmbiGrid/issues/new). :octocat:

## Author:

[Robert Greinacher](mailto:development@robert-greinacher.de?subject=GitHub AmbiGrid) / [@RGreinacher](https://twitter.com/RGreinacher) / [LinkedIn](https://www.linkedin.com/profile/view?id=377637892)

Thank you for reading this and for your interest in my work. I hope I could help you or even make your day a little better. Cheers!

## License:

AmbiGrid is available under the MIT license. See the LICENSE file for more info.
