#!/usr/bin/env python3

import numpy
import re
import sys

inScene         = False

reEnteringScene = r'<SCENE (\d+)>'
reLeavingScene  = r'</SCENE (\d+)>'
reSpeakerStart  = r'<([A-Z\d\s]+)>'
stageDirections = 'STAGE DIR'
allCharacters   = 'ALL'
bothCharacters  = 'BOTH' # FIXME: This should become a regular expression

def isSpecialCharacter(name):
    return    name == stageDirections\
           or name == allCharacters\
           or name == bothCharacters

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
            if not isSpecialCharacter(character):
                characters.add( character )

characterIndices = dict()

for index, character in enumerate(sorted(characters)):
    characterIndices[character] = index

n      = len(characters)
A      = numpy.zeros( (n,n) )

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

            indices = sorted( [ characterIndices[c] for c in charactersInScene ] )
            for i in range(len(indices)):
                for j in range(i+1,len(indices)):
                    u      = indices[i]
                    v      = indices[j]
                    A[u,v] = A[u,v] + 1 # Add a connection between the two vertices
                    A[v,u] = A[u,v]

        elif inScene and re.match(reSpeakerStart, line):
            character = re.match(reSpeakerStart, line).group(1)
            # FIXME: Still require special handling for "all" characters within
            # a scene.
            if not isSpecialCharacter(character):
                charactersInScene.add( character )

nRows, nColumns = A.shape
header          = ";"+";".join( ["\""+character+"\"" for character in sorted(characters ) ] )
characterNames  = sorted(list(characters))

print(header)
for row in range(nRows):
    columnStr = "\""+characterNames[row]+"\""
    for column in range(nColumns):
        columnStr = columnStr + ";" + str(A[row,column])
    print(columnStr)
