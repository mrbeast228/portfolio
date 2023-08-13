import sys

from frontend import Frontend

# frontend based on PyGame
def pyGameFront():
    # init frontend
    frontend = Frontend()

    # render starting board for the first time
    frontend.renderBoard()

    # run main loop
    frontend.loop()

# pseudo-frontend based on REST API (not implemented yet)
def RESTFront():
    pass

# run frontend by default
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'REST':
        RESTFront()
    else:
        pyGameFront()
