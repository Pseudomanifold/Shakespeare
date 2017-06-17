#!/usr/bin/env python3

import networkx as nx
import sys

G     = nx.read_pajek(sys.argv[1])
t     = float(sys.argv[2])
nodes = set()

for source, target, data in G.edges(data=True):
    weight = data['weight']
    if weight <= t:
        nodes.add(source)
        nodes.add(target)

H = G.subgraph(nodes)

nx.write_pajek(H, "/tmp/Subgraph.net")
