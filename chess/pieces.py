from base_classes import Piece, Cell


class Pawn(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'Pawn'
        self.short = 'P'

    def listMoves(self):
        movements = []
        attacks = []

        # check for movements
        fwd = Cell(self.x, self.y + self.color)
        if fwd.envalidPos() and not self.backend.whoOccupies(fwd).color:
            movements.append(fwd)

        # check for attacks
        left = Cell(self.x - 1, self.y + self.color)
        right = Cell(self.x + 1, self.y + self.color)
        for c in left, right:
            if c.envalidPos() and self.isEnemy(self.backend.whoOccupies(c)):
                attacks.append(c)

        self.moves = {'movements': movements, 'attacks': attacks}
