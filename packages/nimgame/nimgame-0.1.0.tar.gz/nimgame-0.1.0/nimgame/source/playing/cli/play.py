"""Play interactive Nim Game in the CLI
"""


from source.core import Nim
from source.typedefs import Move


def play_CLI(
    error_rate: int
) -> None:
    """Play one interactive game

    Create random heaps first. Then, get the user to select who to start.
    Player and Computer take turns until the game ends. Computer will make good
    or bad decisions based on the error rate set in the inctance attribute.
    """
    #create instance, random heaps and display them
    nim = Nim(error_rate)
    nim.setup_heaps()
    print(nim.get_heapstatus(), end='')
    
    while True:
        moveby = input(' First move by? (Auto, Random, Computer, Player): ')
        try:
            #init compturn automatically
            nim.set_start(moveby)
        except ValueError as e:
            print(e)
        else:
            break

    #do moves in a loop, until game end
    while not nim.game_end():
        if nim.activeplayer == 'Computer':
            #make a good decision?
            if nim.make_good_choice():
                #figure out the best move
                move = nim.figure_out_best_move()
            else:
                #set a random (most probably not good) move
                move = nim.get_random_move()
        else:
            while True:
                movestr = input(' Heap?/Straws? ')
                if not len(movestr): continue
                heapnumber = ord(movestr[:1].lower()) - 97
                if heapnumber < 0: continue
                try: removecount = int(movestr[1:])
                except ValueError: continue
                if removecount < 0: continue
                move = Move(heapnumber, removecount)
                break

        try:
            nim.do_move(move)
        except ValueError as e:
            print(e)
            continue
        print(nim.get_heapstatus(), end='')
        if nim.activeplayer == 'Computer': print('')

    #The active player won after the last straw was taken by the opponent
    print(f'{nim.activeplayer} won')
