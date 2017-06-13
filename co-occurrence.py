#!/usr/bin/env python3

import bisect
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
    Enter,       \
    Exit,        \
    Text = range(10)

"""
Checks whether a speaker is a "special" speaker. Special speakers
include the stage directions but also songs and "all" characters
speaking.
"""
def isSpecialSpeaker(name):
    return    name == 'STAGE DIR'\
           or name == 'ALL'\
           or name == 'ALL FOUR'\
           or name == 'BOTH'\
           or name == 'BOTH BROTHERS'\
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
    reActBegin     = r'<ACT (\d+)>'
    reActEnd       = r'</ACT (\d+)>'
    reSpeakerBegin = r'<([A-Z\'\.\d\s]+)>\s+<.*\%>'
    reSpeakerEnd   = r'</([A-Z\'\.\d\s]+)>'
    reEnter        = r'<Enter\s+(\S+)\.>'
    reExit         = r'<Exit(\.?|\s+.*)>'

    if re.match(reDescription, line):
        title = re.match(reDescription, line).group(1).title()
        return LineType.Description, title

    elif re.match(reSceneBegin, line):
        scene = re.match(reSceneBegin, line).group(1)
        return LineType.SceneBegin, scene

    elif re.match(reSceneEnd, line):
        scene = re.match(reSceneEnd, line).group(1)
        return LineType.SceneEnd, scene

    elif re.match(reActBegin, line):
        act = re.match(reActBegin, line).group(1)
        return LineType.ActBegin, act

    elif re.match(reActEnd, line):
        act = re.match(reActEnd, line).group(1)
        return LineType.ActEnd, act

    elif re.match(reSpeakerBegin, line):
        name = re.match(reSpeakerBegin, line).group(1)
        if not isSpecialSpeaker(name):
            # Special handling for singing characters
            if name.endswith("SINGS."):
                name = name[:-6]

            name = name.rstrip()
            return LineType.SpeakerBegin, name

    elif re.match(reSpeakerEnd, line):
        name = re.match(reSpeakerEnd, line).group(1)
        if not isSpecialSpeaker(name):
            return LineType.SpeakerEnd, name

    elif re.match(reEnter, line):
        name = re.match(reEnter, line).group(1)
        return LineType.Enter, name.upper()

    elif re.match(reExit, line):
        exit = re.match(reExit, line).group(1)

        # Remove a trailing dot if the exit direction refers to
        # a named character
        if exit is not "." and exit.endswith("."):
            exit = exit[:-1]

        exit = exit.strip()
        return LineType.Exit, exit

    elif '<' not in line and line.strip():
        return LineType.Text, line.strip()

    return None, None

""""
Class for describing a complete play with weighted co-occurence matrices.
"""
class Play:
    def __init__(self):
        self.characters = list()
        self.title      = None
        self.A          = None # Weighted adjacency matrix

    """ Adds a new character to the play. """
    def addCharacter(self, name):
        if name not in self.characters:
            bisect.insort( self.characters, name )

    """ List characters in alphabetical order. """
    def getCharacters(self):
        return list( self.characters )

    """ Updates an edge in the adjacency matrix """
    def updateEdge(self, name1, name2, w = 1):
        if self.A is None:
            n      = len(self.characters)
            self.A = numpy.zeros( (n,n), dtype=numpy.float_ )

        u = self.characters.index( name1 )
        v = self.characters.index( name2 )

        if u > v:
            u,v = v,u

        self.A[u,v] = self.A[u,v] + w
        self.A[v,u] = self.A[u,v]

    """ Updates multiple edges in the adjacency matrix """
    def updateEdges(self, names, weights):
        for i,first in enumerate(names):
            for j,second in enumerate(names[i+1:]):
                w1 = weights[i]
                w2 = weights[j+i+1]
                self.updateEdge( first, second, w1+w2 )

    """ Checks whether a specified edge exists in the adjacency matrix """
    def hasEdge(self, name1, name2):
        if self.A is None:
            return False

        u = self.characters.index( name1 )
        v = self.characters.index( name2 )

        if u > v:
            u,v = v,u

        return self.A[u,v] > 0

""" Extremely simple way of counting words in a string """
def countWords(line):
    return len( ''.join(c if c.isalnum() else ' ' for c in line).split() )

#
# Extract metadata & all characters
#

play              = Play()
useTimeFiltration = False

# Check whether a time-based filtration is desired
if len(sys.argv) == 3 and sys.argv[2] == '-t':
    useTimeFiltration = True

with open(sys.argv[1]) as f:
    inScene = False
    for line in f:
        t,n = classifyLine(line)

        if t == LineType.Description:
            play.title = n
        elif t == LineType.SceneBegin:
            inScene = True
        elif t == LineType.SceneEnd:
            inScene = False
        elif inScene and t == LineType.SpeakerBegin:
            play.addCharacter(n)
        elif inScene and t == LineType.Enter:
            play.addCharacter(n)

print("Analysing '%s'" % play.title.title())
print("Characters: ")

# Reset the play's title to the filename becase they have a nicer format
# than the actual titles.
play.title = sys.argv[1]
play.title = os.path.basename(play.title)
play.title = os.path.splitext(play.title)[0]

for character in play.getCharacters():
    print("  -", character)

#
# Create co-occurrences
#

with open(sys.argv[1]) as f:
    currentCharacter  = None
    inScene           = False
    activeCharacters  = list()
    wordsPerCharacter = dict()
    firstAppearance   = dict()

    # Elapsed "time" in the play. This is only used for the time-based
    # filtration.
    T = 0

    for line in f:
        t,n       = classifyLine(line)
        needReset = False # Indicates whether current counter variables
                          # need a reset because the scene changed, for
                          # example.

        if t == LineType.SceneBegin:
            inScene = True
        elif t == LineType.SceneEnd:
            inScene   = False
            needReset = True

            #
            # Create weights: Determine the fraction of words used by
            # all active characters.
            #

            numWords = sum( wordsPerCharacter[c]         for c in activeCharacters )
            weights  = [ wordsPerCharacter[c] / numWords for c in activeCharacters ]

            # Create edges between all characters that are still active
            if useTimeFiltration:
                for index,name1 in enumerate(activeCharacters):
                    for name2 in activeCharacters[index+1:]:
                        if not play.hasEdge(name1, name2):
                            t1 = firstAppearance[name1]
                            t2 = firstAppearance[name2]
                            w  = max(t1,t2)
                            play.updateEdge( name1, name2, w )
            else:
                play.updateEdges( activeCharacters, weights )

        elif t == LineType.SpeakerBegin:
            m = re.match( r'.*<(\d+)%>.*', line)
            T = int( m.group(1) )

            if n not in activeCharacters:
                activeCharacters.append(n)
                wordsPerCharacter[n] = 0

            if n not in firstAppearance:
                firstAppearance[n] = T

            currentCharacter = n

        elif t == LineType.Enter:
            if n not in activeCharacters:
                activeCharacters.append(n)
                wordsPerCharacter[n] = 0

            if n not in firstAppearance:
                firstAppearance[n] = T

        elif t == LineType.Exit and currentCharacter:
            # This is the amount of words in the scene that we have seen
            # so far. We require this to assign a weight for the current
            # character that exits the scene.
            numWords = sum( wordsPerCharacter[c] for c in activeCharacters )

            # The current character left the scene
            if n == "." or n == "":
                leavingCharacter = currentCharacter
            # A named character left the scene
            elif n.upper() in activeCharacters:
                leavingCharacter = n.upper()
            else:
                # Check whether the leaving character is a prefix
                # of any named character
                candidates = [ c for c in activeCharacters if c.startswith( n.upper() ) ]
                if len(candidates) == 1:
                    leavingCharacter = candidates[0]
                else:
                    print("Warning: Unable to detect leaving character: '%s'" % n.upper())
                    leavingCharacter = None

            if leavingCharacter:
                for c in activeCharacters:
                    if c is not leavingCharacter:
                        if useTimeFiltration:
                            if not play.hasEdge( leavingCharacter, c ):
                                t1 = firstAppearance[leavingCharacter]
                                t2 = firstAppearance[c]
                                w  = max(t1, t2)
                                play.updateEdge( leavingCharacter, c, w )
                        else:
                            w1 = wordsPerCharacter[leavingCharacter] / numWords
                            w2 = wordsPerCharacter[c]                / numWords
                            play.updateEdge( leavingCharacter, c, w1+w2 )

                if leavingCharacter == currentCharacter:
                    currentCharacter = None

                activeCharacters.remove( leavingCharacter )

        elif t == LineType.Text:
            if not currentCharacter:
                print("Warning: I cannot assign this text to someone: '%s'" % line.strip())
            else:
                wordsPerCharacter[currentCharacter] += countWords(n)

        if needReset:
            currentCharacter  = None
            inScene           = False
            activeCharacters  = list()
            wordsPerCharacter = dict()

#
# Output
#

outputName = play.title.replace(" ", "_") + ".net"

with open(outputName, "w") as f:
    print("%%%s" % play.title, file=f)
    print("*Vertices %d" % len(play.characters), file=f)
    for index, name in enumerate( play.characters ):
        print( "%03d \"%s\"" % ( index+1,name.title() ), file=f )

# Make this an undirected graph
    print("*Edges", file=f)

    nRows, nColumns = play.A.shape

    for row in range(nRows):
        for column in range(row+1,nColumns):
            if play.A[row,column] > 0:
                print( "%03d %03d %f" % (row+1, column+1, play.A[row,column]), file=f )
