#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-



class IssetHelper:

    def isset(self, dictionary, key):
        try:
            dictionary[key]
        except (NameError, KeyError, IndexError):
            return False
        else:
            return True

    def isInt(self, integerValue, base=10):
        if isinstance(integerValue, int):
            return True

        try:
            int(integerValue, base)
        except (ValueError, TypeError):
            return False
        else:
            return True

    def isFloat(self, floatingValue):
        if isinstance(floatingValue, float):
            return True

        try:
            float(floatingValue)
        except (ValueError, TypeError):
            return False
        else:
            return True

    def isValueForIndex(self, array, valueForIndex):
        try:
            array.index(valueForIndex)
        except ValueError:
            return False
        else:
            return True

    def saveIntConvert(self, integerValue, base=10):
        if isinstance(integerValue, int):
            return integerValue
        elif self.isInt(integerValue, base):
            return int(integerValue, base)
        else:
            return -1

    def saveFloatConvert(self, floatValue):
        if isinstance(floatValue, float):
            return floatValue
        elif self.isFloat(floatValue):
            return float(floatValue)
        else:
            return -1.0

    # return a positive (and > 0) integer
    # (the one that comes next in the array) or -1
    def getIntAfterToken(self, array, token, distanceToToken=1):
        if self.isValueForIndex(array, token):
            tokenIndex = array.index(token)
            if (self.isset(array, tokenIndex + distanceToToken) and
                    self.isInt(array[array.index(token) + distanceToToken]) and
                    int(array[array.index(token) + distanceToToken]) >= 0):

                return int(array[array.index(token) + distanceToToken])
        return -1

    # return a positive float (the one that comes next in the array) or -1.0
    def getFloatAfterToken(self, array, token, distanceToToken=1):
        if self.isValueForIndex(array, token):
            tokenIndex = array.index(token)
            if (self.isset(array, tokenIndex + distanceToToken) and
                    self.isFloat(array[array.index(token) + distanceToToken]) and
                    float(array[array.index(token) + distanceToToken]) >= 0):

                return float(array[array.index(token) + distanceToToken])
        return -1.0

    # return a positive float (the one that comes next in the array) or -1.0
    def getStringAfterToken(self, array, token, distanceToToken=1):
        if self.isValueForIndex(array, token):
            tokenIndex = array.index(token)
            if self.isset(array, tokenIndex + distanceToToken):
                return array[tokenIndex + distanceToToken]

        return ''
