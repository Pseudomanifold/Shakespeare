#!/usr/bin/env python

import re
import sys

scene = ""

reEnteringScene = r'<SCENE (\d+)>'
reLeavingScene  = r'</SCENE (\d+)>'
reSpeakerStart  = r'<([A-Z])+>'

characters = set()

with open(sys.argv[1]) as f:
    currentCharacters = set()
    for line in f:
        if re.match(reEnteringScene, line):
            currentCharacters = set()
            print("Entering scene")
        elif re.match(reLeavingScene, line):
            print("Leaving scene")
            characters.union( currentCharacters )
        elif re.match(reSpeakerStart, line):
            print(line)
