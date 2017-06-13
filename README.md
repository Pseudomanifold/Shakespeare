This repository contains the code used to extract co-occurrence networks
from a tagged corpus of Shakespeare's plays.

The networks have been analysed using *persistent homology*, a technique
from computational topology. Please refer to our paper

[*Shall I compare thee to a network?* &ndash; Visualizing the Topological Structure of Shakespeare's Plays](http://bastian.rieck.ru/research/Vis2016.pdf)

for more details.

# Data

* The folder `Corpus` contains the original corpus that was used to
  calculate co-occurrence networks. Additional information about the
  amount of speech between certain characters has been added. Please
  refer to [lexically.net](http://lexically.net/wordsmith/support/shakespeare.html) for the original data.
* The folder `Networks` contains the co-occurrence networks for all the
  plays that we used in the paper. Networks are categorized into
  *speech-based* and *time-based* filtrations. Please refer to the paper
  for more details.
* The folder `Plays` contains the corrected variants of the plays,
  sorted into three broad categories.

# Usage

The main script is called `co-occurrence.py`. Given the filename of
a tagged play, it automatically produces a co-occurrence network using
the *speech-based filtration* we described in the paper. The network
will be stored in the current directory. To batch-process all networks
automatically, you could for example use:

    find ./Plays/ -name "*.txt" -exec ./co-occurrence.py {} \;

This traverses the folder `Plays` and executes the extraction script for
every file. If you want the *time-based filtration* instead, use the
parameter `-t`, i.e.:

    find ./Plays/ -name "*.txt" -exec ./co-occurrence.py {} -t \;

Again, this will result in a set of networks. Note that all existing
networks will be overwritten in the current folder.

# Licence

The data and the code is are released under an MIT licence. Please refer
to the file `LICENSE` for more information.
