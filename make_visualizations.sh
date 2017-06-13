#!/usr/bin/env zsh
#
# Visualizes all speech-based networks and places the resulting files in
# /tmp.

INDEX=0

for file in Networks/Speech/*.net; do
  echo "Visualizing ${file:r}..."
  INDEX=$(($INDEX+1))
  FILE=$(printf "/tmp/%02d.tex" $INDEX)
  ./visualize_network.py ${file} > $FILE
done
