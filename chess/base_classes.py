# create our own exception for chess project
class ChessBackendException(Exception):
    def __init__(self, salary, message="Something went wrong"):
        self.salary = salary
        self.message = message
        super().__init__(self.message)


# base class of cell
class Cell:
    x = -1
    y = -1
    long = 'Empty'
    short = '.'

    def __init__(self, x, y):
        self.move(x, y)

    def envalidPos(self, **kwargs):
        if 'x' in kwargs and 'y' in kwargs:
           return kwargs['x'] > -1 and kwargs['y'] > -1 and kwargs['x'] < 8 and kwargs['y'] < 8
        return self.x > -1 and self.y > -1 and self.x < 8 and self.y < 8

    def isEnemy(self, piece):
        return False

    def move(self, x, y):
        self.x = x
        self.y = y

    def isPiece(self):
        return hasattr(self, 'color')


# base class with chess piece
class Piece(Cell):
    color = 0
    backend = None
    moves = None

    def __init__(self, x, y, color, backend):
        super().__init__(x, y) # init cell

        # envalid self
        if not self.envalidPos():
            raise ChessBackendException('Invalid piece position')

        # envalid color
        if color not in [-1, 1]:
            raise ChessBackendException('Invalid piece color')
        self.color = color # set color

        self.backend = backend # link to global backend

        # create list of moves
        self.listMoves()

    # check if piece is enemy
    def isEnemy(self, piece):
        return piece.isPiece() and self.color == -piece.color

    # basic function of getting list of available cells for movements and attacks, to be edited
    def listMoves(self):
        self.moves = {'movements': [], 'attacks': []}

    # basic function for any piece to move itself
    def changePos(self, x, y):
        possible = False

        for cell in self.moves['movements']:
            if cell.envalidPos() and cell.x == x and cell.y == y:
                self.move(x, y)
                possible = True

        for cell in self.moves['attacks']:
            if cell.envalidPos() and cell.x == x and cell.y == y:
                self.backend.removePiece(cell)
                self.move(x, y) # always move only after removal!
                possible = True

        self.listMoves()
        return possible
