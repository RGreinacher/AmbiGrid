#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-


class ColorCalculator:

    def convertHexColorToRgb(self, hexColor):
        redChannel = (hexColor & 0xff0000) >> 16
        greenChannel = (hexColor & 0x00ff00) >> 8
        blueChannel = (hexColor & 0x0000ff)
        return (redChannel, greenChannel, blueChannel)

    # each channel: int, 0..255
    def convertRgbToHexColor(self, redChannel, greenChannel, blueChannel):
        hexValue = 0
        hexValue = hexValue | redChannel << 16
        hexValue = hexValue | greenChannel << 8
        hexValue = hexValue | blueChannel
        return hexValue

    def convertRgbToLightness(self, redChannel, greenChannel, blueChannel):
        redNormalized = redChannel / 255
        greenNormalized = greenChannel / 255
        blueNormalized = blueChannel / 255

        minNormalizedValue = min(
            redNormalized, greenNormalized, blueNormalized)
        maxNormalizedValue = max(
            redNormalized, greenNormalized, blueNormalized)

        return (maxNormalizedValue + minNormalizedValue) / 2

    # thanks to http://www.easyrgb.com/index.php?X=MATH
    def convertRgbToHsl(self, redChannel, greenChannel, blueChannel):
        redNormalized = redChannel / 255
        greenNormalized = greenChannel / 255
        blueNormalized = blueChannel / 255

        minNormalizedValue = min(
            redNormalized, greenNormalized, blueNormalized)
        maxNormalizedValue = max(
            redNormalized, greenNormalized, blueNormalized)
        deltaMinMaxNormalizedValue = maxNormalizedValue - minNormalizedValue

        lightness = (maxNormalizedValue + minNormalizedValue) / 2
        # lightness = math.sqrt(0.299 * pow(redChannel, 2) + 0.587 * pow(greenChannel, 2) + 0.114 * pow(blueChannel, 2))

        if deltaMinMaxNormalizedValue == 0:
            hue = 0
            saturation = 0
        else:
            if lightness < 0.5:
                saturation = deltaMinMaxNormalizedValue / \
                    (maxNormalizedValue + minNormalizedValue)
            else:
                saturation = deltaMinMaxNormalizedValue / \
                    (2 - maxNormalizedValue - minNormalizedValue)

            deltaRed = (((maxNormalizedValue - redNormalized) / 6) +
                        (deltaMinMaxNormalizedValue / 2)) / deltaMinMaxNormalizedValue
            deltaGreen = (((maxNormalizedValue - greenNormalized) / 6) +
                          (deltaMinMaxNormalizedValue / 2)) / deltaMinMaxNormalizedValue
            deltaBlue = (((maxNormalizedValue - blueNormalized) / 6) +
                         (deltaMinMaxNormalizedValue / 2)) / deltaMinMaxNormalizedValue

            if redNormalized == maxNormalizedValue:
                hue = deltaBlue - deltaGreen
            elif greenNormalized == maxNormalizedValue:
                hue = (1 / 3) + deltaRed - deltaBlue
            elif blueNormalized == maxNormalizedValue:
                hue = (2 / 3) + deltaGreen - deltaRed

            if hue < 0:
                hue = hue + 1
            elif hue > 1:
                hue = hue - 1

        return (hue, saturation, lightness)

    def convertHslToHexColor(self, hue, saturation, lightness):
        (r, g, b) = self.convertHslToRgb(hue, saturation, lightness)
        return self.convertRgbToHexColor(r, g, b)

    # # thanks to http://www.easyrgb.com/index.php?X=MATH
    def convertHslToRgb(self, hue, saturation, lightness):
        if saturation == 0:
            redChannel = greenChannel = blueChannel = int(lightness * 255)
        else:
            if lightness < 0.5:
                lightnessIntermediate2 = lightness * (1 + saturation)
            else:
                lightnessIntermediate2 = (
                    lightness + saturation) - (lightness * saturation)

            lightnessIntermediate1 = (2 * lightness) - lightnessIntermediate2

            redChannel = int(
                255 * self.convertHueToRgb(lightnessIntermediate1, lightnessIntermediate2, hue + (1 / 3)))
            greenChannel = int(
                255 * self.convertHueToRgb(lightnessIntermediate1, lightnessIntermediate2, hue))
            blueChannel = int(
                255 * self.convertHueToRgb(lightnessIntermediate1, lightnessIntermediate2, hue - (1 / 3)))

        return (redChannel, greenChannel, blueChannel)

    # thanks to http://www.easyrgb.com/index.php?X=MATH
    def convertHueToRgb(self, lightness1, lightness2, hue):
        if hue < 0 or hue > 1:
            if hue < 0:
                hue = hue + 1
            elif hue > 1:
                hue = hue - 1
            return self.convertHueToRgb(lightness1, lightness2, hue)

        if (6 * hue) < 1:
            return lightness1 + ((lightness2 - lightness1) * 6 * hue)
        if (2 * hue) < 1:
            return lightness2
        if (3 * hue) < 2:
            return lightness1 + ((lightness2 - lightness1) * ((2 / 3) - hue) * 6)
        return lightness1

    def convertHexColorToHSL(self, hexColor):
        (redChannel, greenChannel, blueChannel) = self.convertHexColorToRgb(
            hexColor)
        return self.convertRgbToHsl(redChannel, greenChannel, blueChannel)

    def frameRgbValue(self, value):
        if value > 255:
            return 255
        elif value < 0:
            return 0
        else:
            return value

    # brightness: double, 0..1
    def setBrightnessToRgbColor(self, redChannel, greenChannel, blueChannel, targetLightness):
        (hue, saturation, lightness) = self.convertRgbToHsl(
            redChannel, greenChannel, blueChannel)
        (redChannel, greenChannel, blueChannel) = self.convertHslToRgb(
            hue, saturation, targetLightness)

        redChannel = self.frameRgbValue(redChannel)
        greenChannel = self.frameRgbValue(greenChannel)
        blueChannel = self.frameRgbValue(blueChannel)

        return (redChannel, greenChannel, blueChannel)

    # brightness: double, 0..1
    def setBrightnessToHexColor(self, hexColor, targetLightness):
        (redChannel, greenChannel, blueChannel) = self.convertHexColorToRgb(
            hexColor)
        (redChannel, greenChannel, blueChannel) = self.setBrightnessToRgbColor(
            redChannel, greenChannel, blueChannel, targetLightness)
        return self.convertRgbToHexColor(redChannel, greenChannel, blueChannel)

    # transforms the rgb color values into a common HTML hex format
    def getHtmlHexStringFromRgbColor(self, redChannel, greenChannel, blueChannel):
        redChannelAsHex = hex(redChannel)
        redChannelAsHex = redChannelAsHex[2:]
        if len(redChannelAsHex) == 1:
            redChannelAsHex = '0' + redChannelAsHex
        hexString = redChannelAsHex

        greenChannelAsHex = hex(greenChannel)
        greenChannelAsHex = greenChannelAsHex[2:]
        if len(greenChannelAsHex) == 1:
            greenChannelAsHex = '0' + greenChannelAsHex
        hexString = hexString + greenChannelAsHex

        blueChannelAsHex = hex(blueChannel)
        blueChannelAsHex = blueChannelAsHex[2:]
        if len(blueChannelAsHex) == 1:
            blueChannelAsHex = '0' + blueChannelAsHex
        hexString = hexString + blueChannelAsHex

        return '#' + hexString
