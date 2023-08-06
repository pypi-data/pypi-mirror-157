"""Demonstrate the features of the package with a small interactive execution

The "import __init__ as nimgame" simulates, as if the "nimgame" package was
imported after installation, so that elements like the Nim class can be used as
"nimgame.Nim"
"""


import __init__ as nimgame


try:
    while True:
        testtype = input(
            'Press '
            '"m" for running multiple games'
            '; '
            '"p" for playing an interactive game'
            '; '
            '"w" for running the web server'
            ': '
        )

        if testtype=='m':
            #do the test with 1000 games
            gamecount = 1000
            #request 10% Computer and 30% Player error rate
            error_rate = nimgame.ErrorRate(Computer=10, Player=30)
            #run all tests
            from tests import testruns
            testruns.run_many_games(gamecount, error_rate)
            break
        
        elif testtype=='p':
            nimgame.play_CLI(error_rate=10)
            break
        
        elif testtype=='w':
            nimgame.playweb()
            break

except KeyboardInterrupt:
    print('\nGame terminated by the user pressing Ctrl-C')
