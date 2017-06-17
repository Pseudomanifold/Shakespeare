#!/usr/bin/env python3

import networkx as nx
import sys

G = nx.read_gml( sys.argv[1] )
d = G.degree()

degrees = dict()
for node in sorted( d.keys() ):
    degree          = d[node]
    degrees[degree] = degrees.get(degree, 0) + 1

for x in sorted( degrees.keys() ):
    y = degrees[x]
    print("%d\t%d" % (x,y))
