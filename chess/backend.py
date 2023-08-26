import copy
import json

from pieces import *
from base_classes import ChessBackendException


class Backend:
    # init game backend
    def __init__(self):
        # init variables
        # human player color
        self.playerColor = 0

        # list of all pieces on board
        self.pieces = []

        # current board in 2-dimensional list
        self.currentBoard = []

        # whose move
        self.currentMove = 1

        # state of game
        #  -1 - black won
        #   1 - white won
        #   2 - draw
        #   0 - game is on
        self.gameState = 0

        # which piece need to be transformed
        self.toTransform = None

        # which piece was previous acting (needed for pawns)
        self.previousActing = None

        # create basic location of pieces
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
    # find a king by color
    def findKing(self, color):
        return [piece for piece in self.pieces if piece.__class__ == King and piece.color == color][0]

    # check if cell is beaten by color
    def isBeaten(self, cell, color):
        placeToFind = 'attacks' if hasattr(cell, 'color') and cell.color else 'movements'
        for piece in self.pieces:
            if piece.color == color and cell in piece.moves[placeToFind]:
                return True
        return False

    # check for check :)
    def isCheck(self):
        king = self.findKing(self.currentMove)
        return self.isBeaten(king, -self.currentMove)

    # check for stalemate
    def isStalemate(self):
        movesAllowed = False
        for piece in self.pieces:
            if movesAllowed:
                break
            if piece.color == self.currentMove:
                for move in piece.moves['movements'] + piece.moves['attacks']:
                    currentMoveAvailable = piece.changePos(move.x, move.y, dryRun=True)
                    if currentMoveAvailable:
                        movesAllowed = True
                        break
        return not movesAllowed

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
    def action(self, org, dst, force=False):
        # check for game is on
        if self.gameState:
            return False

        # make an action
        piece = self.whoOccupies(Cell(org))
        result = piece.setCoords(dst, force=force)

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
    def transformPawn(self, destType='Queen'):
        # check for pawn can be transformed
        if not self.toTransform:
            return False

        # backup pawn coords
        x = self.toTransform.x
        y = self.toTransform.y
        color = self.toTransform.color

        # check for valid type of piece
        g = globals()
        if destType in g:
            self.removePiece(self.toTransform)
            self.addPiece(g[destType](x, y, color, self))
            self.toTransform = None
            return True
        else:
            raise ChessBackendException('Invalid type of piece!')

    # release castling
    def releaseCastling(self, org, dst):
        if org.__class__ == King and abs(org.x - dst.x) == 2 and org.countOfMoves == 0:
            # check for free and non-beaten cells between king and rook
            if org.x < dst.x\
                    and self.whoOccupies(Cell(6, dst.y)).color == 0 and not self.isBeaten(Cell(6, dst.y), -self.currentMove)\
                    and self.whoOccupies(Cell(6, dst.y)).color == 0 and not self.isBeaten(Cell(6, dst.y), -self.currentMove)\
                    and self.whoOccupies(Cell(5, dst.y)).color == 0 and not self.isBeaten(Cell(5, dst.y), -self.currentMove):
                # right rook
                rook = self.whoOccupies(Cell(7, dst.y))
                self.action(rook, Cell(5, dst.y), force=True)

                self.action(org, dst, force=True)
                self.currentMove *= -1
                return True
            elif org.x > dst.x\
                    and self.whoOccupies(Cell(3, dst.y)).color == 0 and not self.isBeaten(Cell(3, dst.y), -self.currentMove)\
                    and self.whoOccupies(Cell(2, dst.y)).color == 0 and not self.isBeaten(Cell(2, dst.y), -self.currentMove)\
                    and self.whoOccupies(Cell(1, dst.y)).color == 0 and not self.isBeaten(Cell(1, dst.y), -self.currentMove):
                # left rook
                rook = self.whoOccupies(Cell(0, dst.y))
                self.action(rook, Cell(3, dst.y), force=True)

                self.action(org, dst, force=True)
                self.currentMove *= -1
                return True
        return False
