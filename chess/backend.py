import copy
import json

from pieces import *
from base_classes import ChessBackendException


class Backend:
    # list of all pieces on board
    pieces = []

    # current board in 2-dimensional list
    currentBoard = []

    # backup board for moves availability checking
    reservedBoard = None

    # whose move
    currentMove = 1

    # state of game
    #  -1 - black won
    #   1 - white won
    #   2 - draw
    #   0 - game is on
    gameState = 0

    # which piece need to be transformed
    toTransform = None

    # create basic location of pieces
    def __init__(self):
        for props in [[0, 1], [7, -1]]: # X coord and color
            # rooks
            self.addPiece(Rook(0, props[0], props[1], self))
            self.addPiece(Rook(7, props[0], props[1], self))

            # knights
            self.addPiece(Knight(1, props[0], props[1], self))
            self.addPiece(Knight(6, props[0], props[1], self))

            # bishops
            self.addPiece(Bishop(2, props[0], props[1], self))
            self.addPiece(Bishop(5, props[0], props[1], self))

            # queen and king
            self.addPiece(Queen(3, props[0], props[1], self))
            self.addPiece(King(4, props[0], props[1], self))

            # pawns
            for i in range(8):
                self.addPiece(Pawn(i, props[0] + props[1], props[1], self))

        self.generateBoard()  # don't forget it after all actions!

    # add new piece to board
    def addPiece(self, piece):
        if piece and not self.whoOccupies(piece).color:
            self.pieces.append(piece)
        self.generateBoard()  # don't forget it after all actions!

    # remove piece from board (when beaten)
    def removePiece(self, cell):
        toRemove = self.whoOccupies(cell)
        if toRemove.color:
            self.pieces.remove(toRemove)
        self.generateBoard()  # don't forget it after all actions!

    # reload board
    def overrunBoard(self):
        for piece in self.pieces:
            piece.listMoves()

    # generate 2-dimension list for native integration
    def generateBoard(self):
        self.overrunBoard()
        board = [[Cell(i, j) for i in range(8)] for j in range(8)]

        for piece in self.pieces:
            board[piece.y][piece.x] = piece
        self.currentBoard = board

    # render board for REST API integration
    # mode 0: print to stdout (debug)
    #      1: dump JSON (API)
    def renderBoard(self, mode=1):
        subResult = [[cell.createText() for cell in row]for row in self.currentBoard]
        if mode:
            return json.dumps(subResult)
        for row in subResult:
            print(row)

    # return piece occupies cell if exists
    def whoOccupies(self, cell):
        checking = copy.copy(cell)
        checking.__class__ = Piece
        checking.color = 0

        if checking in self.pieces:
                return self.pieces[self.pieces.index(checking)] # return piece which "equals" to cell
        return checking

    # checkmates mechanics
    def backupBoard(self):
        self.reservedBoard = copy.deepcopy(self.currentBoard)

    def restoreBoard(self):
        self.currentBoard = copy.deepcopy(self.reservedBoard)
        self.reservedBoard = None

    # find a king by color
    def findKing(self, color):
        return [piece for piece in self.pieces if piece.__class__ == King and piece.color == color][0]

    # check for check :)
    def isCheck(self):
        king = self.findKing(self.currentMove)
        for piece in self.pieces:
            if king in piece.moves['attacks'] and king.isEnemy(piece):
                return True
        return False

    # check for stalemate
    def isStalemate(self):
        for piece in self.pieces:
            if piece.color == self.currentMove and piece.moves['movements'] + piece.moves['attacks']:
                return False
        return True

    # check for checkmate
    def isCheckmate(self):
        return self.isCheck() and self.isStalemate()

    # check if only kings left on board (draw)
    def isOnlyKings(self):
        for piece in self.pieces:
            if piece.__class__ != King:
                return False
        return True

    # make a move
    def action(self, org, dst):
        # check for game is on
        if self.gameState:
            return False

        # make an action
        piece = self.whoOccupies(Cell(org))
        result = piece.setCoords(dst)

        # regenerate board
        self.generateBoard()

        # check for pawn-conversion
        if result and piece.__class__ == Pawn and piece.y in [0, 7]:
            self.toTransform = piece

        # check if game is ended
        if self.isCheckmate():
            self.gameState = -self.currentMove
        elif self.isStalemate() or self.isOnlyKings():
            self.gameState = 2
        return result

    # 2-dimensional list of moves
    # mode 0: print to stdout (debug)
    #      1: dump JSON (API)
    def renderMoves(self, org, mode=1):
        return self.whoOccupies(Cell(org)).renderBeats(mode)

    # transform pawn to queen/rook/bishop/knight
    def transformPawn(self, destType):
        g = globals()

        x = self.toTransform.x
        y = self.toTransform.y
        color = self.toTransform.color

        self.removePiece(self.toTransform)
        if destType in g:
            self.addPiece(g[destType](x, y, color, self))
        else:
            raise ChessBackendException('Invalid type of piece!')
