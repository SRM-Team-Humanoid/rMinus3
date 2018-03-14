#!/usr/bin/env python
import rospy
import time
import numpy as np
import anglereader




reader = anglereader.AngleReader('angles.json')

angles = reader.parse("7 Scratch head")

for angle in angles:
    print angle

print "\n\n\n"


angleset = reader.setparse("5 Push up")
for angles in angleset:
    for angle in angles:
        print angle


