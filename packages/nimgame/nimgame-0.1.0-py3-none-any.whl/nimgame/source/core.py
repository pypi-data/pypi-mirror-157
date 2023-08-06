"""The Nim Game core

This main class implements the init and maintenance of heaps, movements of
straws, records the statuses and calculates decisions.
"""


from dataclasses import dataclass
from typing import Union, Tuple, ClassVar
import functools
import itertools
import random; random.seed()
from source.typedefs import Move, ErrorRate
from source import calculations


@dataclass
class Nim(calculations.Mixin):
    """Class to implement the Nim game

    Methods:
    - setup_heaps(): initiate the heaps. Note that this creates the heaps
        instance attribute, i.e. there is no need for __init__()
    - set_start(): set which party is to start the game
    - do_move(): do a move, either the Computer's or the Player's turn
    - get_heapstatus(): get the heap status (straws in heaps)
    - game_end(): figure out whether the game ended
    - calculation methods from the mixin

    Attributes:
        heaps (list): it contans the number of straws in each heap. This is
            initiated in setup_heaps().
        activeplayer (str): either the "Computer" or "Player"; or "start" in the
            beginning
        nextturn (iterator.__next__): calling it infinitely yields the swapped
            player names

    Args:
        error_rate: The rate percentage of mistakes the Computer is to make. By
            deafult it is 0%, i.e. the computer never makes mistakes, and the
            Player has no chance to win (unless the Player decides who to start
            and never makes mistakes). If it was set to the extreme 100%, the
            Computer would always intentionally make wrong moves, practically
            making all attempts to lose. NB, if the Player does the same, the
            Computer may still win.
            For testing, when moves of both parties are made by the program,
            the error rate of both parties can be set with the "ErrorRate"
            namedtuple. This can be used to create staistics of games played by
            different skilled players. NB, still, the 1st party will be reported
            in the results as Computer, and the 2nd as Player, just to name
            them.
        heapcount_range: The min and max number of heaps to be set up. Less than
            3 heaps makes little sense, more than 15 is a bit of an overkill.
            So, the default is (3-15), but it can be set otherwise.
        strawcount_range: The min and max number of strwas to be set up in a
            heap. Less than 1 straw makes no sense, more than 20 is a bit of an
            overkill. So, the default is (1-20).
        misere: Whether it is the "misère" version of the game.
    """
    error_rate: Union[int, ErrorRate]=0
    heapcount_range: Tuple[int, int]=(3, 15)
    strawcount_range: Tuple[int, int]=(1, 20)
    misere: bool=True
    
    activeplayer: ClassVar[str]='start'
    nextturn: ClassVar=itertools.cycle(('Computer', 'Player')).__next__
    
    
    def setup_heaps(self, 
        heapcounts: list=None
    ) -> None:
        """Initial setup of heaps of straws
        
        Args:
            heapcounts: list elements state the number of straws in each heap.
                If no list is provided, a random number of heaps are created
                with random number of straws.
        """
        #random heaps to be created?
        if not heapcounts:
            heapcounts = []
            #create a random int for the number of heaps
            heapnumber = random.randint(*self.heapcount_range)
            for _ in range(heapnumber):
                #create a random int for the number of straws in the heap
                strawcount = random.randint(*self.strawcount_range)
                #create the heap with the number of straws
                heapcounts.append(strawcount)
        else:
            heapnumber = len(heapcounts)
            if heapnumber not in range(*self.heapcount_range):
                raise ValueError(
                    f"The number of heaps({heapnumber}) is out of "
                    f"the {self.heapcount_range} range"
                )
            for idx, heap in enumerate(heapcounts):
                if heap not in range(*self.strawcount_range):
                    raise ValueError(
                        f"The number of straws({heap}) in heap#{idx} "
                        f"is out of the {self.strawcount_range} range"
                    )

        #create the heaps list
        self.heaps = heapcounts


    def set_start(self, 
            myturn: Union[str, bool]='a'
    ) -> None:
        """Set the starting party
        
        User can explicitly set which party is to start. This makes sense if
        this decision is made based on the starting heap status.
        
        The user can also ask for random selection.
        
        By default the computer makes the decision using 2 factors. First it
        figures out whether the heap status is beneficial for starting. i.e. it
        is a winning status. Then it checks the required error rate and it
        intentionally makes a wrong decision with higher likelihood if the
        error_rate is higher.
        
        Note:
            The myturn argument is internally converted to a boolean if it
            arrives as a str. The myturn value is used in a bool context, i.e.
            it can be any type (e.g. empty list will act like a False, i.e.
            Computer is to start). No issues with "overwriting" it as the
            default remains the 'a' for subsequent calls and also the outer
            variable, where the argument comes from, remains unaffected.
        
        Args:
            myturn: the logical value from the Player's point of view.
                - 'a' (by default): the Computer figures out which party is to start
                    the game, based on the heap counts and the required error_rate
                - truthy or 'p': Player
                - falsy or 'c': Computer
                - 'r': random
        """
        #auto?
        if myturn=='a':
            #figure out whether the initial heap status is good for the Computer
            winning = self.is_winning_for_next()
            #whether to make a good decision
            smart = self.make_good_choice()
            
            #winning&smart or !winning&!smart makes the Computer start
            myturn = winning ^ smart
        
        #random?
        elif myturn=='r':
            myturn = random.choice([True, False])
        
        #map c to False, p to True
        elif isinstance(myturn, str):
            myturn = myturn.lower()
            if myturn=='c':
                myturn = False
            elif myturn=='p':
                myturn = True
            else:
                raise ValueError(f'"myturn" has an unknown value: "{myturn}"')
        
        #Player's turn needed?
        if myturn:
            #the cycle starts by the Computer, so get rid of it
            self.nextturn()
        #get the next player
        self.activeplayer = self.nextturn()


    def do_move(self, 
        move: Move
    ) -> None:
        """Remove given number of straws from a given heap
        
        Before doing the straw removal, check for illegal moves and report
        issues. After the given number of straws have been removed from a given
        heap, swap the turn of players.

        Args:
            move: the serial number of the heap, starting from 0 and the number
                of straws to remove from that heap, in a namedtuple
        """
        if len(self.heaps)-1 < move.heapnumber:
            raise ValueError(
                f'Wrong heap letter ({chr(move.heapnumber+97)}), there are '
                f'A-{chr(len(self.heaps)+97)} heaps only'
            )

        if self.heaps[move.heapnumber] < move.removecount:
            raise ValueError(
                f'Heap({chr(move.heapnumber+97)}) only has '
                f'{self.heaps[move.heapnumber]} straw(s), '
                f'cannot remove {move.removecount}'
            )

        #reduce the required heap
        self.heaps[move.heapnumber] -= move.removecount

        #get the next player
        self.activeplayer = self.nextturn()


    def get_heapstatus(self) -> str:
        """Get the heap status in a formatted string
        
        Returns:
            The number of straws per heap. Also header at the start.
        """
        status = ''
        #at the start?
        if self.activeplayer == 'start':
            #start with the heading line
            status = ' '.join([f' {chr(65+a)}' for a in range(len(self.heaps))]) + '\n'
        #list the straws in the heaps, single-digit numbers padded with space
        status += ' '.join([f'{str(h):>2}' for h in self.heaps])
        
        return status
    

    def game_end(self) -> bool:
        """Identify whether the game ended, i.e. all heaps are empty

        Use the functools.reduce() on the heaps list, with a True initializing
        value and keep it true as long as the number of straws is zero.
        
        Returns:
            The flag to indicate game end.
        """
        return functools.reduce(
            lambda x,y: x&(y==0),
            self.heaps,
            True
        )
