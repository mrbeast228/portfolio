import copy

from pieces import *


class Backend:
    pieces = []
    currentBoard = []

    def __init__(self):
        self.addPiece(Pawn(0, 0, 1, self))
        self.addPiece(Pawn(1, 1, -1, self))
        self.generateBoard()  # don't forget it after all actions!

    def addPiece(self, piece):
        if piece.isPiece() and not self.whoOccupies(piece).color:
            self.pieces.append(piece)
        self.generateBoard()  # don't forget it after all actions!

    def removePiece(self, cell):
        toRemove = self.whoOccupies(cell)
        if toRemove.color:
            self.pieces.remove(toRemove)
        self.generateBoard()  # don't forget it after all actions!

    def overrunBoard(self):
        for piece in self.pieces:
            piece.listMoves()

    def generateBoard(self):
        self.overrunBoard()
        board = [[Cell(i, j) for i in range(8)] for j in range(8)]

        for piece in self.pieces:
            board[piece.y][piece.x] = piece
        self.currentBoard = board

    def renderBoard(self):
        return [[cell.short for cell in row]for row in self.currentBoard]

    def whoOccupies(self, cell):
        checking = copy.copy(cell)
        checking.__class__ = Piece
        checking.color = 0

        for piece in self.pieces:
            if piece.x == checking.x and piece.y == checking.y:
                return piece
        return checking
