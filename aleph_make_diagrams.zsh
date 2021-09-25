#!/usr/bin/env zsh

ALEPH_DIR=$HOME/Projects/Aleph
ALEPH_BUILD_DIR=$ALEPH_DIR/build

NETWORK_ANALYSIS_BINARY=$ALEPH_BUILD_DIR/examples/network_analysis
SPLIT_OUTPUT_BINARY=$ALEPH_DIR/utilities/split_output.py

OUTPUT_DIR=/tmp

for file in $argv; do
  OUTPUT=${file:t:r}".txt"
  $NETWORK_ANALYSIS_BINARY $file 2  > $OUTPUT_DIR/$OUTPUT
  $SPLIT_OUTPUT_BINARY --prefix=d --digits=1 $OUTPUT_DIR/$OUTPUT
done
