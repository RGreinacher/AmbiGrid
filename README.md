# AmbiGrid

Raspberry Pi & Arduino controlled RGB LED matrix mood light.

## The quick look:

### Why?


### How?


### What?


## How it's made


## Get it running
Just install [Python3](https://www.python.org/downloads/) and the [Daemonize](https://github.com/thesharp/daemonize) module:

	pip3 install daemonize

This is required to provide the server as a daemon. All other required modules come Python3 per default.
Run the server with default parameters (not a daemon, port 4444):

	python3 sleepServer.py

You can customize the port by adding a flag:

	python3 sleepServer.py -p 1337

Or start the server as a daemon and run in the backgound:

	python3 sleepServer.py -d

You can even enable a verbous mode to get informed about nearly everything that happens on the inside:

	python3 sleepServer.py -v

And you can ask for the list of possible options with:

	python3 sleepServer.py -h

(You won't need administration privileges to run AmbiGrid if you use port numbers above 1023)

***

# API usage:
The whole API uses only HTTP GET requests to keep things simple and make it easy to test.
(Future versions may change that to make use of HTTP PUT, PATCH and UPDATE, as well as be able to specify an API version.
The pattern for API versioning will be `sleepApi/1.0/[task]`. This pattern can already be implemented by clients now, but will not affect the behaviour.)

The response format is always JSON. Possible HTTP status codes are 200, 202, 400 and 404.
Every request returns either an acknowledgement and the current status, just the current status or an error message.

### quick'n'dirty

ambiGridApi/status -> {status: ANIMATION_NAME, baseColor: #FF0099, clockColor: #00FF99, baseLightness: [0..1], clockLightness: [0..1], currentFPS: [0..100] [, fadeOutIn: [int]]]}
ambiGridApi/setAnimation/ANIMATION_NAME -> {STATUS}
ambiGridApi/setFadeOut/[int]] -> {STATUS}
ambiGridApi/stopFadeOut -> {STATUS}
ambiGridApi/setBaseColor/hex/FF0099 -> {STATUS}
ambiGridApi/setBaseColor/rgb/[0..255]/[0..255]/[0..255] -> {STATUS}
ambiGridApi/setBaseColor/lightness/[0..100] -> {STATUS}
ambiGridApi/setClockColor/hex/FF0099 -> {STATUS}
ambiGridApi/setClockColor/rgb/[0..255]/[0..255]/[0..255] -> {STATUS}
ambiGridApi/setClockColor/lightness/[0..100] -> {STATUS}

## get status information
	call: sleepApi/status
	receive: {'status': 'running', 'currentVolume': [decimal]} (HTTP: 200)
	receive: {'status': 'goingToSleep', 'timeToSleep': '[int]', 'currentVolume': [decimal]} (HTTP: 200)
	receive: {'status': 'goingToSilence', 'timeToSilence': '[int]', 'currentVolume': [decimal]} (HTTP: 200)
	receive: {'status': 'goingToSleepAndSilence', 'timeToSleep': '[int]', 'currentVolume': '[decimal]'} (HTTP: 200)

## set the sleep time / immediate sleep

Set only the sleep time:

	call: sleepApi/setSleepTime/[int]
	receive: {'status': 'goingToSleep', 'timeToSleep': '[int]'} (HTTP: 202)
	receive error: {'error': 'bad sleep time'} (HTTP: 400)

Set immediate sleep:

	call: sleepApi/immediateSleep
	receive: {'status': 'immediateSleep'} (HTTP: 202)


## set the silence time / volume

Set the volume (percentage, decimal):

	call: sleepApi/setVolume/[decimal]
	receive: {'status': 'running', 'currentVolume': [decimal]} (HTTP: 202)
	receive: {'status': 'goingToSleep', 'timeToSleep': '[int]', 'currentVolume': [decimal]} (HTTP: 200)
	receive error: {'error': 'bad volume percentage'} (HTTP: 400)
	receive error: {'error': 'volume is auto-controlled'} (HTTP: 400)

Set only the silence time:

	call: sleepApi/setSilenceTime/[int]
	receive: {'status': 'goingToSilence', 'timeToSilence': '[int]'} (HTTP: 202)
	receive error: {'error': 'bad silence time'} (HTTP: 400)

## set good night time

The good night time is a combination of both, the sleep and the silence time. If this time is greater than 10 minutes, the time until then will be at a constant volume and it will be turned down only within the last 10 minutes. If the good night time is shorter than 10 minutes the volume will be decreased linearly from the beginning of the call.

	call: sleepApi/setGoodNightTime/[int]
	receive: {'status': 'goingToSleepAndSilence', 'timeToSleep': '[int]', 'currentVolume': '[decimal]'} (HTTP: 202)
	receive error: {'error': 'bad good night time'} (HTTP: 400)


## unset timer / reset the server:

Use one command for unsetting all timers and resetting the server. This command will be executed every time before a request is processed, except for the `setVolume` command and the `status` command:

	call: sleepApi/reset
	receive: {'status': 'running', 'currentVolume': [decimal]} (HTTP: 202)
	receive: {'status': 'running', 'acknowledge': 'unsettingTimer', 'currentVolume': [decimal]} (HTTP: 202)

## others:
	call: [any other request]
	receive error: {'error': 'wrong address, wrong parameters or no such resource'} (HTTP: 404)

### Test calls:
- [status request](http://localhost:4444/sleepApi/status) http://localhost:4444/sleepApi/status
- [set sleep time](http://localhost:4444/sleepApi/setSleepTime/42) http://localhost:4444/sleepApi/setSleepTime/42
- [set immediate sleep](http://localhost:4444/sleepApi/immediateSleep) http://localhost:4444/sleepApi/immediateSleep
- [set silence time](http://localhost:4444/sleepApi/setSilenceTime/42) http://localhost:4444/sleepApi/setSilenceTime/42
- [set good night time](http://localhost:4444/sleepApi/setGoodNightTime/42) http://localhost:4444/sleepApi/setGoodNightTime/42
- [set system volume](http://localhost:4444/sleepApi/setVolume/75.8) http://localhost:4444/sleepApi/setVolume/75.8
- [unset timer](http://localhost:4444/sleepApi/reset) http://localhost:4444/sleepApi/reset

***

# Apart of the code

## Contribution & Contributors

I'd love to see your ideas for improving this project!
The best way to contribute is by submitting a pull request or a [new Github issue](https://github.com/RGreinacher/AmbiGrid/issues/new). :octocat:

## Author:

[Robert Greinacher](mailto:network@robert-greinacher.de?subject=GitHub AmbiGrid) / [@RGreinacher](https://twitter.com/RGreinacher) / [LinkedIn](https://www.linkedin.com/profile/view?id=377637892)

Thank you for reading this and for your interest in my work. I hope I could help you or even make your day a little better. Cheers!

## License:

AmbiGrid is available under the MIT license. See the LICENSE file for more info.

*[Thanks [Tom](https://github.com/TomKnig) for the inspiration of this last passage.]*
