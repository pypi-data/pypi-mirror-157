"""The Game of Nim


Rules:
------

For the general description of the Nim and similar games, see the
`Wikipedia page`_.

This game is played by 2 palyers (the computer can be a player).
There are straws arranged in heaps.
There may be any number of heaps and any number of straws in a heap.

Players take turns. In each turn, a player takes straws from 1 heap.
It must be at least 1 straw. There is no upper limit (but the heap size).

There are 2 types of games:
- the "normal" where the player, who takes the last straw, wins
- the `"misère" game`_, where the player, who has to take the last straw, loses


Usage:
------

import nimgame
nim = nimgame.Nim(error_rate=10)  #request 10% error rate from the Computer
nim.setup_heaps()  #create heaps randomly
nim.set_start(myturn=True)  #indicate that the Player wants to start
nim.do_move(2, 4)  #remove 4 straws from heap #2
...


Package content
---------------

- Modules "core" and "calculations" in "source" provide the Nim class and its
    methods.
- Modules under the "playing" directory can be run to play the game in CLI.
- Modules in "tests" provide automatic test runs playing several games.
- A special module "__main__" in the root directory runs when the package is
    called. It provides some interactions for executing automatic runs or
    interactive games.


.. _Wikipedia page: https://en.wikipedia.org/wiki/Nim
.. _misère game: https://en.wikipedia.org/wiki/Mis%C3%A8re#Mis%C3%A8re_game
"""

# Version of the package
__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)


# Make sure the package base path is in the module import path (e.g. for flit)
import sys, os
basepath = os.path.dirname(__file__)
if basepath not in sys.path:
    sys.path.insert(0, basepath)

# Make the Nim class available on package level
from source.core import Nim
# Make structures for error rate and move available on package level
from source.typedefs import ErrorRate, Move

# Make the playing functions available on package level
from source.playing.cli.play import play_CLI
from source.playing.web.play import playweb
