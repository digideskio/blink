#!/usr/bin/python
"""
blink.py -- a high-level 'blink(1)' API by Marco Pashkov
Based on Aaron Blondeau's demo -> https://github.com/todbot/blink1/tree/master/python/blink1hid-demo.py

Version 0.2 - Feb 21. 2013
"""

import usb  ### requires pyusb
            # https://github.com/walac/pyusb
            # + "brew install libusb" on osx 
            # + libusb-win32 (inf method) on windows
import string
from time import sleep
from morse import morse_code

COLORS = {
    "red" : (255,0,0),
    "green" : (0,255,0),
    "blue" : (0,0,255),
    "white" : (255,255,255),
    "black" : (0,0,0),
}

class Blink(object):
    """Simple python controller for a single 'blink' device"""

    def __init__(self, fps=30):
        """initiate the blink device - set the fps - 'frames per second'"""
        self.dev = usb.core.find(idVendor=0x27b8, idProduct=0x01ed)
        assert self.dev is not None, "Could not find blink device."
        self.bmRequestTypeOut = usb.util.build_request_type(usb.util.CTRL_OUT, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
        self.bmRequestTypeIn = usb.util.build_request_type(usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
        self.framesPerSecond = fps

    def _sanityCheck(self, color):
        """return a sane color value - between 0 and 255"""
        return max(0, min(255,color))

    def _transferCommand(self, action, color=(0,0,0), th=0, tl=0):
        """internal method to transfer a command to the blink device
            #The Blink1 takes 8 bytes of input
            # 1=report_id (0)
            # 2=action (c = fade to rgb, n = set rgb now)
            # 3=red
            # 4=green
            # 5=blue
            # 6=th : time/cs high (T >>8)  where time 'T' is a number of 10msec ticks
            # 7=tl : time/cs low (T & 0xff)
            # 8=step (0)"""

        red, green, blue = color
        _red = self._sanityCheck(red)
        _green = self._sanityCheck(green)
        _blue = self._sanityCheck(blue)
        self.dev.ctrl_transfer(self.bmRequestTypeOut, 0x09, (3 << 8) | 0x01, 0, [0x00, action, _red, _green, _blue, th, tl, 0x00, 0x00])

    def blink(self, color=(COLORS["red"]), count=5, fps=5):
        """let the device blink"""
        old_fps = self.framesPerSecond
        self.framesPerSecond = fps
        for i in range(count):
            self.setColor(color)
            self.turnOff()

        self.framesPerSecond = old_fps

    def fadeColor(self, color=(0,0,0), sec=1, blocking=True):
        """fade to a new color"""
        T = (sec * 1000)/10        ###<sec> seconds worth of 10msec tics
        th = (T & 0xff00) >> 8
        tl = T & 0x00ff
        self._transferCommand(action=0x63, color=color, th=th, tl=tl)
        if blocking:
            sleep(sec)

    @property
    def framesPerSecond(self):
        return self._framesPerSecond

    @framesPerSecond.setter
    def framesPerSecond(self, value):
        """sets the 'frames per second' - this value paces the setColor function by making it a blocking function - if set to None it is not blocking"""
        assert value > 0, "fps - 'frames per second' must be bigger than 0 - given:{0}".format(fps)
        self._framesPerSecond = value

    def _morseLetter(self, char):
        long_time = 0.5
        short_time = 0.25
        if char in morse_code:
            code = [short_time if c else long_time for c in morse_code[char]]
            for c in code:
                self.setColor(COLORS["red"])
                sleep(c)
                self.turnOff()
                sleep(short_time)
        else:
            self.turnOff()
        sleep(long_time)

    def morse(self, text_raw):
        text = text_raw.lower()
        [self._morseLetter(l) for l in text]

    def setColor(self, color=(0,0,0)):
        """sets the color immediately"""
        self._transferCommand(0x6E, color=color)
        if self.framesPerSecond is not None:
            sleep(1.0/self.framesPerSecond)

    def turnOff(self):
        """turn the LEDs off"""
        self.setColor(COLORS["black"])

    @property
    def version(self):
        """return device firmware version"""
        self._transferCommand(action=0x76)
        sleep(.05)
        version_raw = self.dev.ctrl_transfer(self.bmRequestTypeIn, 0x01, (3 << 8) | 0x01, 0, 8)
        version = ''.join(chr(i) for i in version_raw) # items in the array should correspond to ascii codes for something like "v 100"
        version = filter(lambda x: x in string.printable, version)
        return version #the c code must tack on an extra 0?


def main():
    """example, how to use the wrapper"""

    ### initalize a blink object
    blink = Blink()

    ### how to use the blink object...
    print "blink firmware version: {0}".format(blink.version)
    # blink.blink(count=5)

    blink.morse("sos")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "goodbye..."
