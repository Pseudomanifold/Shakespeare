#!/usr/bin/env python3

import igraph
import os
import sys

filenames = sys.argv[1:]
for filename in filenames:
    g       = igraph.read(filename, format="pajek")
    n       = g.vcount()
    density = g.ecount() / (n*(n-1)/2)

    print("\"%s\"\t%f\t%d" % (os.path.splitext(filename)[0], density, g.vcount() ) )
