import json
import string


# create our own exception for chess project
class ChessBackendException(Exception):
    def __init__(self, salary, message="Something went wrong"):
        self.salary = salary
        self.message = message
        super().__init__(self.message)


# base class of cell
class Cell:
    def __init__(self, *args):
        # init variables
        self.x = -1
        self.y = -1
        self.color = 0
        self.long = 'Empty'
        self.short = 'E'

        # setup cell
        largs = len(args)

        if largs == 1:
            if type(args[0]) is list:
                self.move(args[0][0], args[0][1])
            elif type(args[0]) is str:
                self.__init__(Cell.classicCoords(args[0]))
            elif hasattr(args[0], '__class__') and issubclass(args[0].__class__, Cell):
                self.move(args[0].x, args[0].y)
            else:
                raise ChessBackendException("Invalid position")
        elif largs == 2:
            self.move(args[0], args[1])
        else:
            raise ChessBackendException("Invalid position")

    # assume cells as equal when their coords are equal
    def __eq__(self, other):
        return hasattr(other, 'x') and hasattr(other, 'y') and self.x == other.x and self.y == other.y

    # check cell is in 8x8 board
    def envalidPos(self, **kwargs):
        if 'x' in kwargs and 'y' in kwargs:
           return kwargs['x'] > -1 and kwargs['y'] > -1 and kwargs['x'] < 8 and kwargs['y'] < 8
        return self.x > -1 and self.y > -1 and self.x < 8 and self.y < 8

    # check some piece is our enemy (always False for bare cell)
    def isEnemy(self, piece):
        return False

    # set our coords
    def move(self, x, y):
        self.x = x
        self.y = y

    # create description of piece for API
    def createText(self):
        return 'Empty_empty'

    # function "is cell a piece"
    def __bool__(self):
        return bool(hasattr(self, 'color') and self.color)

    # convert coords to classic (A2, B4)
    @staticmethod
    def classicCoords(coords):
        return [string.ascii_uppercase.index(coords[0]), int(coords[1]) - 1]

    # vector sum
    def __add__(self, other):
        if hasattr(other, 'x') and hasattr(other, 'y'):
            return Cell(self.x + other.x, self.y + other.y)
        return self


# base class with chess piece
class Piece(Cell):
    def __init__(self, x, y, color, backend):
        # init variables
        self.moves = None
        self.countOfMoves = 0

        # init cell
        super().__init__(x, y)

        # envalid self
        if not self.envalidPos():
            raise ChessBackendException('Invalid piece position')

        # envalid and set color
        if color not in [-1, 1]:
            raise ChessBackendException('Invalid piece color')
        self.color = color

        # link to global backend
        self.backend = backend

        # create list of moves
        self.listMoves()

    # check if piece is enemy
    def isEnemy(self, piece):
        return piece.envalidPos() and piece and self.color == -piece.color

    # basic function of getting list of available cells for movements and attacks, to be edited
    def listMoves(self):
        self.moves = {'movements': [], 'attacks': []}

    # en passant remover, will work only for pawns
    def enPassant(self, backupPos):
        pass

    # basic function for any piece to move itself (or check movement availability)
    def changePos(self, x, y, dryRun=False):
        cell = Cell(x, y)
        backupPiece = self.backend.whoOccupies(cell)
        backupPos = [self.x, self.y]

        if not self.backend.gameState and self.backend.currentMove == self.color and cell.envalidPos() and cell in self.moves['movements'] + self.moves['attacks']:
            if cell in self.moves['attacks']:
                self.backend.removePiece(cell)
            self.move(x, y)
            # check for en passant (for pawns)
            self.enPassant(backupPos)

            # check is movement available from point of view of the rules of checkmates
            self.backend.overrunBoard()
            checkStatus = self.backend.isCheck()

            # virtual movements mechanics
            if checkStatus or dryRun:
                # cancel last movement if it leads with check or dryRun enabled
                if cell in self.moves['attacks']:
                    self.backend.addPiece(backupPiece)
                self.move(backupPos[0], backupPos[1])
                self.backend.overrunBoard()
            else:
                self.backend.currentMove *= -1
                self.countOfMoves += 1
                self.backend.previousActing = self
            return not checkStatus
        return False

    # for classic coords
    def setCoords(self, coords, force=False):
        moveFunc = self.move if force else self.changePos
        if type(coords) is str:
            pos = self.classicCoords(coords)
            return moveFunc(pos[0], pos[1])
        elif type(coords) is list:
            return moveFunc(coords[0], coords[1])
        elif hasattr(coords, '__class__') and issubclass(coords.__class__, Cell):
            return moveFunc(coords.x, coords.y)
        raise ChessBackendException('Invalid action!')

    # create text-description for debug & API "rendering"
    def createText(self):
        color = ''
        if self.color == 1:
            color = 'white'
        elif not self.color:
            color = 'empty'
        else:
            color = 'black'

        return '_'.join([self.short, color])

    # 2-dimensional list of moves
    # mode 0: print to stdout (debug)
    #      1: dump JSON (API)
    def renderBeats(self, mode):
        board = [['' for i in range(8)] for j in range(8)]

        board[self.y][self.x] = 'O'
        for m in self.moves['movements']:
            board[m.y][m.x] = '+'
        for a in self.moves['attacks']:
            board[a.y][a.x] = 'X'

        if mode:
            return json.dumps(board)
        for row in board:
            print(row)
