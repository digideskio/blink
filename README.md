blink(1) Python api
===================

This is a simple, open source python-wrapper for the [blink(1)](http://thingm.com/products/blink-1.html) device by [thingm](http://thingm.com/). It is based on Aaron Blondeau's [demo](https://github.com/todbot/blink1/tree/master/python/blink1hid-demo.py)

Installation
-----------

Currently just download the files or clone the git and put the library into your Python project. In the future I might add a setup.py for an easy global installation.

Usage
-----
	
	from blink import Blink, COLORS
	blink = Blink()

	### setting the device to a color
	blink.setColor(COLORS["red"])	### setting pre-defined colors
	blink.setColor((0,255,0))		### setting (red, green, blue) values directly as a tuple

	### fade to a new color
	blink.fadeColor(COLORS["blue"], sec=3)

	### let the blink(1) blink  :-)
	blink.blink()

	### morse some text
	blink.morse("hello world")

    