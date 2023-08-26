import json
import requests


# write AI using requests to chess.com API
class AI:
    def __init__(self, backend):
        self.backend = backend

    def makeMove(self):
        # TODO(): make AI
        self.backend.renderBoard()
        return False
