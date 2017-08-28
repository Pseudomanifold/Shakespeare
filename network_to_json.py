#!/usr/bin/env python3

import json
import sys

import networkx as nx

"""
Normalizes a name by replacing spaces by dots. This ensures that node
names may be parsed more easily.
"""
def normalize(name):
  return name.replace(" ", ".")

filename = sys.argv[1]
G        = nx.read_pajek(filename)

nodes = []

for name in G.nodes():
  nodes.append( { 'id': normalize(name), 'degree': G.degree(name) } )

links = []

for source,target,weight in G.edges(data='weight'):
  links.append(\
    {\
      'source': normalize(source),
      'target': normalize(target),
      'weight': weight
    }
  )

data = { 'nodes': nodes, 'links': links }
json.dump(data, sys.stdout)
