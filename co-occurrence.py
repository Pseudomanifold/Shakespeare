#!/usr/bin/env python3

import re
import sys

inScene = False

reEnteringScene = r'<SCENE (\d+)>'
reLeavingScene  = r'</SCENE (\d+)>'
reSpeakerStart  = r'<([A-Z\d\s]+)>'
stageDirections = 'STAGE DIR'
allCharacters   = 'ALL'


characters = set()
edges      = set()

#
# Extract all characters
#

with open(sys.argv[1]) as f:
    for line in f:
        if re.match(reEnteringScene, line):
            inScene           = True
        elif re.match(reLeavingScene, line):
            inScene = False
        elif inScene and re.match(reSpeakerStart, line):
            character = re.match(reSpeakerStart, line).group(1)
            characters.add( character )

#
# Create basic graph output
#

print("graph G\n"
      "{\n")

for index,character in enumerate(sorted(characters)):
    print("%d [label='%s'];" % (index, character))

#
# Extract co-occurences
#

with open(sys.argv[1]) as f:
    charactersInScene = set()
    for line in f:
        if re.match(reEnteringScene, line):
            inScene           = True
            charactersInScene = set()
        elif re.match(reLeavingScene, line):
            inScene = False
            print("Characters in the current scene:", file=sys.stderr)
            for character in sorted(charactersInScene):
                print("  - %s" % character, file=sys.stderr)

            c = list(sorted(characters))
            i = [ c.index(character) for character in sorted(charactersInScene) ]
            for u in i:
                for v in i:
                    if u < v:
                        print( "%d -- %d;" % (u,v) )

        elif inScene and re.match(reSpeakerStart, line):
            character = re.match(reSpeakerStart, line).group(1)
            # FIXME: Still require special handling for "all" characters within
            # a scene.
            if character != stageDirections and character != allCharacters:
                charactersInScene.add( character )

#
# Close graph
#

print("}")
