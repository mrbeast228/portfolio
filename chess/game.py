import sys
import threading
from pygame import quit

from frontend import Frontend


games = []

# frontend based on PyGame
def pyGameFront():
    # ask user for his color
    playerColor = 1 if Frontend.tkinterChoiceBox(choice=['White', 'Black'], prompt='Choose your color') == 'White' else -1

    # init frontend
    frontend = Frontend(playerColor=playerColor)

    # add to list of games
    global games
    games.append(frontend)

    # render starting board for the first time
    frontend.renderBoard()

    # run main loop
    frontend.loop()

    # remove from list of games
    games.pop()

    # force close window (on threading)
    try:
        quit()
    except Exception:
        pass
    return

# pseudo-frontend based on REST API (not implemented yet)
def RESTFront():
    pass

# run game in background using threads
def runBackground():
    global games
    if games:
        print('Only one instance of game can be run at the same time now!')
        return

    threading.Thread(target=(RESTFront if len(sys.argv) > 1 and sys.argv[1] == 'REST' else pyGameFront)).start()

# run game in foreground using console
def runConsole():
    (RESTFront if len(sys.argv) > 1 and sys.argv[1] == 'REST' else pyGameFront)()

# run game by default
if __name__ == '__main__':
    runConsole()
