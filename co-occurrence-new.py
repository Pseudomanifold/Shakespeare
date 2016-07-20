#!/usr/bin/env python3

import numpy
import os
import re
import sys

"""
Describes the type of line, i.e. whether a scene starts, an act starts,
an speaker starts, and so on.
"""
class LineType:
    Description, \
    SceneBegin,  \
    SceneEnd,    \
    ActBegin,    \
    ActEnd,      \
    SpeakerBegin,\
    SpeakerEnd,  \
    Exit = range(8)

"""
Checks whether a speaker is a "special" speaker. Special speakers
include the stage directions but also songs and "all" characters
speaking.
"""
def isSpecialSpeaker(name):
    return    name == 'STAGE DIR'\
           or name == 'ALL'\
           or name == 'BOTH'\
           or name == 'SONG.'

"""
Classifies a line and returns the line type. 'None' indicates that the
line type is unspecified.

Returns a tuple with the line type and the first extracted token, e.g.
the name of the speaker, the name of the play, and so on. Again, this
token is allowed to be 'None'.
"""
def classifyLine(line):
    reDescription  = r'<\s+Shakespeare\s+--\s+(.+)\s+>'
    reSceneBegin   = r'<SCENE (\d+)>'
    reSceneEnd     = r'</SCENE (\d+)>'
    reActStart     = r'<ACT (\d+)>'
    reActEnd       = r'</ACT (\d+)>'
    reSpeakerBegin = r'<([A-Z\.\d\s]+)>'
    reSpeakerEnd   = r'</([A-Z\.\d\s]+)>'
    reExit         = r'<Exit(\.?|\s+.*)>'

    if re.match(reDescription, line):
        title = re.match(reDescription, line).group(1).title()
        return (LineType.Description, title)

    elif re.match(reSceneBegin, line):
        scene = re.match(reSceneBegin, line).group(1)
        return (LineType.SceneBegin, scene)

    elif re.match(reActBegin, line):
        act = re.match(reActBegin, line).group(1)
        return (LineType.ActBegin, act)

    elif re.match(reActEnd, line):
        act = re.match(reActEnd, line).group(1)
        return (LineType.ActEnd, act)

    elif re.match(reSpeakerBegin, line):
        name = re.match(reSpeakerBegin, line).group(1)
        if not isSpecialSpeaker(name):
            return (LineType.SpeakerBegin, name)

    elif re.match(reSpeakerEnd, line):
        name = re.match(reSpeakerEnd, line).group(1)
        if not isSpecialSpeaker(name):
            return (LineType.SpeakerEnd, name)

    elif re.match(reExit, line):
        exit = re.match(reExit, line).group(1)
        return (LineType.Exit, exit)

    return (None,None)

""""
Class for describing a complete play with weighted co-occurence matrices.
"""
class Play:
    def __init__(self):
        characters = dict()

def isSpecialCharacter(name):
    return    name == stageDirections\
           or name == allCharacters\
           or name == bothCharacters\
           or name == "SONG." # FIXME

inScene         = False

reEnteringScene   = r'<SCENE (\d+)>'
reLeavingScene    = r'</SCENE (\d+)>'
reActStart        = r'<ACT (\d+)>'
reActEnd          = r'</ACT (\d+)>'
reSpeakerStart    = r'<([A-Z\.\d\s]+)>'
rePlayDescription = r'<\s+Shakespeare\s+--\s+(.+)\s+>'
reExitUnnamed     = r'<Exit\.?>'

stageDirections = 'STAGE DIR'
allCharacters   = 'ALL'
bothCharacters  = 'BOTH' # FIXME: This should become a regular expression

title      = ""
characters = set()
edges      = set()

#
# Extract all characters
#

with open(sys.argv[1]) as f:
    for line in f:
        if re.match(rePlayDescription, line):
            title = re.match(rePlayDescription, line).group(1).title()
        elif re.match(reEnteringScene, line):
            inScene           = True
        elif re.match(reLeavingScene, line):
            inScene = False
        elif inScene and re.match(reSpeakerStart, line) and not re.match(reActStart, line):
            character = re.match(reSpeakerStart, line).group(1)
            if not isSpecialCharacter(character):
                characters.add( character )

print("Characters: ")

for character in characters:
    print("  -", character)

characterIndices = dict()

for index, character in enumerate(sorted(characters)):
    characterIndices[character] = index

n      = len(characters)
A      = numpy.zeros( (n,n), dtype=numpy.float_ )

#
# Extract co-occurences
#

with open(sys.argv[1]) as f:
    charactersInScene = set()
    wordsPerCharacter = dict()
    currentCharacter  = None
    numWordsInScene   = 0

    for line in f:
        if re.match(reEnteringScene, line):
            inScene           = True
            charactersInScene = set()
            wordsPerCharacter = dict()
            currentCharacter  = None
            numWordsInScene   = 0
        elif re.match(reLeavingScene, line):
            inScene = False
            print("Characters in the current scene:", file=sys.stderr)
            for character in sorted(charactersInScene):
                print("  - %s" % character, file=sys.stderr)

            x = sorted( [ (characterIndices[c], wordsPerCharacter[c]) for c in charactersInScene ], key=lambda t: t[0] )
            for i in range(len(x)):
                for j in range(i+1,len(x)):
                    u      = x[i][0]
                    v      = x[j][0]
                    w      = ( x[i][1] + x[j][1] ) / numWordsInScene
                    A[u,v] = A[u,v] + w # Increase weight
                    A[v,u] = A[u,v]

        elif inScene and re.match(reSpeakerStart, line) and not re.match(reActStart, line):
            character = re.match(reSpeakerStart, line).group(1)
            # FIXME: Still require special handling for "all" characters within
            # a scene.
            if not isSpecialCharacter(character):
                currentCharacter = character
                charactersInScene.add( character )

        elif inScene and re.match(reExitUnnamed, line):
            indices = sorted( [ characterIndices[c] for c in charactersInScene ] )
            u       = characterIndices[currentCharacter]
            w       = wordsPerCharacter[currentCharacter] / numWordsInScene
            for i in range(len(indices)):
                v      = indices[i]
                A[u,v] = A[u,v] + w # Increase weight
                A[v,u] = A[u,v]

            print(currentCharacter, "left the scene.")
            charactersInScene.remove(currentCharacter)

        elif '<' not in line and line.strip():
            numWords        = len( ''.join(c if c.isalnum() else ' ' for c in line).split() )
            numWordsInScene = numWordsInScene + numWords
            if currentCharacter:
                wordsPerCharacter[ currentCharacter ] = wordsPerCharacter.get( currentCharacter, 0 ) + numWords

#
# Output
#

outputName = title.replace(" ", "_") + ".net"

with open(outputName, "w") as f:
    print("%%%s" % title, file=f)
    print("*Vertices %d" % len(characters), file=f)
    for index, name in enumerate( sorted(characters) ):
        print( "%d \"%s\"" % ( index+1,name.title() ), file=f )

# Make this an undirected graph
    print("*Edges", file=f)

    nRows, nColumns = A.shape
    characterNames  = sorted(list(characters))

    for row in range(nRows):
        for column in range(row+1,nColumns):
            if A[row,column] > 0:
                print( "%03d %03d %f" % (row+1, column+1, A[row,column]), file=f )
