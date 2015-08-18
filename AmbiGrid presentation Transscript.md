# The AmbiGrid - Video transcript

Hi, this is Robert Greinacher and I want to introduce to you the **AmbiGrid** project - an open source programmable color LED mood light with a fast web socket interface.

## Inspiration - The why

The Inspiration was kind of like what Philips did with it’s *Wake up light*: I wanted to build a light which can help me to fall asleep or to wake up again by illustrating a sunrise or a sunset - or which accompanies my everyday life with smooth animations. And of course I want to control it with my computer / phone / tablet / whatever. I think this kind of gadget is the perfect toy for me.

Needless to say there are many products out there you can buy like Wifi enabled light bulbs which I could utilize to do exactly what I described. But I remembered that years ago I tried the *AdaLight project* from *Adafruit* which adds a DIY *AmbiLight* to your computer screen; so I already head an Arduino with a USB interface and a strand of color LEDs. And at this point my engineering ambitions caught me so I had to find out what I could do with it.

## What I built

What I built is a compact product with a 49 pixel screen which only has one cable - the power plug. Each pixel is powered by one RGB LED which could be addressed separately. In combination this grid of LEDs forms a little screen with not only the same color all over it but with the possibility to show a light play. 

That’s the reason why I call it **AmbiGrid**: It is a ambient light, arranged as a grid. Referrings to a product called *AmbiLight* are sheer occasional. ;)

It’s wooden case hides all the technics. It auto-connects to the local wifi and starts the controlling software on it’s own, providing a web app which connects via web sockets to the animations software and gives users the ability to adjust animations or colors with there smartphone or any other web capable device.

The web app is made with simplicity in mind. Every touch on a button or a slider has direct impact on the light. It provides a color preview and some information like the overall lightness or the current frame rate. The color is changed via either combining the three primary colors red, green and blue, or via a color space called HSL whereby you change the hue, the saturation or the lightness separately.

Besides the web app let you select and adjust all the available animations like the *color change* which moves to every color or the *pulsing circle* which literally shows a pulsing circle. This animation appears very relaxing and I like falling asleep with this showing smooth, warm colors. To do so the web app provides a *fade out* animations as well, which can be combined with any of the other animations.

## How it’s made - technically speaking

I started the project with understanding the source code of the *Adalight project* to learn how to communicate with the *Adruino*. After that I started writing a little *Python* framework to generalize the communication to the LEDs and for writing different animations. I wanted to create a central software unit to take care of the hardware, the animations, different settings, the frame rate, incoming requests from clients and steadily updating them about colors or how much time is left until the light faded out. At last I wrote a HTTP server unit to even serve the controlling web app on my own.

This software runs on a *Raspberry Pi* in the inside of the **AmbiGrid** case. Every calculation is done there, and it’s doing good: 55 frames per seconds in average is enough to display animations fluently. This *Raspberry Pi* is on the one hand connected to the wifi network and on the other to the LED controlling *Arduino* via USB. So the software writes an array of RGB values for every pixel to the serial port for every frame - 55 times every second.

Because I need a color calculations module for the animations, the web app doesn’t calculate anything on it’s own. Instead it just sends *JSON* encoded data via the web socket connection to the **AmbiGrid**, which applies the request and responds itself with a status *JSON* containing the new calculated color values. The web socket connection is so fast, that even this ping pong doesn’t seem to have any latency - leastwise in the local network.

The software has a dry run mode, so if there is no *Arduino* connected, it still serves the web app which you can play around with and test the web socket connection.

## Awesome, I want to build my own

What would you need to start building this on your own? The easiest way is to order all the stuff I listed in the description. This is exactly my setup. But this has grown over time and may not be the most cost efficient. You can get rid of the Arduino for example by controlling the LEDs right via the GPIO ports of the Raspberry Pi (consider some soldering skills because you will have to use 5V signals for the chip in the LED strands but the Raspberry Pi’s GPIO output will only provide 3,3V - but that is not a problem, how tos are out there). Or you could use cheeper LEDs with the WS2811 driver chip; that would require a little source code modification but that should not be too difficult.

The software needs Python 3.5 or greater with some free and open source packages installed; the GitHub page explains what you need to launch it.

The part that you can’t buy or download is the wooden case. I have no CAD files and made the plan for it right before I started building it. But as there is no right or wrong I’m sure you will find a way build your LED matrix.

## Contact & good bye

If there are any questions left just contact me; you’ll find my Twitter, GitHub and Mail right below the video. I’m looking forward to discuss your plans.

Thanks for watching and good night (fade out the light of the **AmbiGrid**).

***

## Below the video

The **AmbiGrid** project by Robert Greinacher, 2015.

Twitter: **@RGreinacher** / GitHub: **RGreinacher** / Mail: **development@robert-greinacher.de**

Thanks to my Dad who helped me with the case, Mr. Schmidutz from the Karl-Arnold-Schule Biberach, and Mr. Moll from Uttenweiler for some wood and the frosted glas.

### Sources & links

- [**AmbiGrid** source code on GitHub](https://github.com/RGreinacher/AmbiGrid)
- [Adalight project by Adafruit](https://learn.adafruit.com/adalight-diy-ambient-tv-lighting)

### Used tech parts & components

Raspberry Pi components:

- [Raspberry Pi 2](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/) (the first generation will work too)
- [power supply](http://www.amazon.de/gp/product/B00IMU7TF4) (any compatible will do)
- [SD card](http://www.amazon.de/gp/product/B00MWXUK08) (any compatible will do)
- [Wifi stick](http://www.amazon.de/gp/product/B00LLIOT34) (any compatible will do)

Arduino & LEDs:

- [Arduino Uno R3](http://www.adafruit.com/products/50)
- [Standard USB-A-B cable](http://www.adafruit.com/products/62) (any compatible will do)
- [RGB LEDs with power supply](http://www.adafruit.com/product/461) (use WS2801 powered LEDs for the code as it is)
- [more RGB LEDs](http://www.adafruit.com/products/322)

Other:

- [slim multi socket](http://www.amazon.de/gp/product/B00406W0VC) (any compatible will do)
