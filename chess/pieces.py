from base_classes import Piece, Cell


class Pawn(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'Pawn'
        self.short = 'P'

    def enPassant(self, backupPos):
        if self.__class__ == Pawn and self.x != backupPos[0]:
            self.backend.removePiece(Cell(self.x, backupPos[1]))

    def listMoves(self):
        movements = []
        attacks = []

        # check for movements
        fwd = Cell(self.x, self.y + self.color)
        if fwd.envalidPos() and not self.backend.whoOccupies(fwd):
            movements.append(fwd)

        # check for first action
        first = Cell(self.x, self.y + 2 * self.color)
        if first.envalidPos() and not self.backend.whoOccupies(first) and self.countOfMoves == 0:
            movements.append(first)

        # check for attacks
        left = Cell(self.x - 1, self.y + self.color)
        right = Cell(self.x + 1, self.y + self.color)
        for c in left, right:
            if c.envalidPos() and self.isEnemy(self.backend.whoOccupies(c)):
                attacks.append(c)

        # check for en passant
        for direction in [-1, 1]:
            check = self.backend.whoOccupies(Cell(self.x + direction, self.y))
            if check.envalidPos() and check and check.__class__ == Pawn and self.backend.previousActing == check and check.countOfMoves == 1 and check.color == -self.color:
                attacks.append(Cell(self.x + direction, self.y + self.color))

        self.moves = {'movements': movements, 'attacks': attacks}

class Knight(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'Kinght'
        self.short = 'K'

    def listMoves(self):
        movements = []
        attacks = []

        # check 8 Г movements
        for x in [-1, 1]:
            for y in [-1, 1]:
                for orient in [-1, 1]:
                    cell = self + Cell([x, 2 * y][::orient])
                    if cell.envalidPos() and not self.backend.whoOccupies(cell):
                        movements.append(cell)
                    elif self.isEnemy(self.backend.whoOccupies(cell)):
                        attacks.append(cell)

        self.moves = {'movements': movements, 'attacks': attacks}

class Bishop(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'Bishop'
        self.short = 'B'

    def listMoves(self):
        movements = []
        attacks = []

        # check 4 diagonal movements
        for x in [-1, 1]:
            for y in [-1, 1]:
                distance = 1

                while True:
                    cell = Cell(x * distance, y * distance) + self
                    if not cell.envalidPos() or self.backend.whoOccupies(cell):
                        break
                    movements.append(cell)
                    distance += 1

                toBeCheckedOnEnemy = Cell(x * distance, y * distance) + self
                if self.isEnemy(self.backend.whoOccupies(toBeCheckedOnEnemy)):
                    attacks.append(toBeCheckedOnEnemy)

        self.moves = {'movements': movements, 'attacks': attacks}

class Rook(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'Rook'
        self.short = 'R'

    # check 4 straight movements
    def listMoves(self):
        movements = []
        attacks = []

        # check 4 diagonal movements
        for dir in [-1, 1]:
            for coord in [0, 1]:
                distance = 1

                while True:
                    move = [0, 0]
                    move[coord] = distance * dir
                    cell = Cell(move) + self
                    if not cell.envalidPos() or self.backend.whoOccupies(cell):
                        break
                    movements.append(cell)
                    distance += 1

                move = [0, 0]
                move[coord] = distance * dir
                toBeCheckedOnEnemy = Cell(move) + self
                if self.isEnemy(self.backend.whoOccupies(toBeCheckedOnEnemy)):
                    attacks.append(toBeCheckedOnEnemy)

        self.moves = {'movements': movements, 'attacks': attacks}

class Queen(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'Queen'
        self.short = 'Q'

    def listMoves(self):
        # concatenate from bishop and rook
        Bishop.listMoves(self)
        bishop = self.moves

        Rook.listMoves(self)
        rook = self.moves

        movements = bishop['movements'] + rook['movements']
        attacks = bishop['attacks'] + rook['attacks']

        self.moves = {'movements': movements, 'attacks': attacks}

class King(Piece):
    def __init__(self, x, y, color, backend):
        super().__init__(x, y, color, backend) # init piece
        self.long = 'King'
        self.short = 'W'

    def listMoves(self):
        movements = []
        attacks = []

        # check near
        for x in range(-1, 2):
            for y in range(-1, 2):
                cell = Cell(x, y) + self
                if cell.envalidPos() and not self.backend.whoOccupies(cell):
                    movements.append(cell)
                if self.isEnemy(self.backend.whoOccupies(cell)):
                    attacks.append(cell)

        self.moves = {'movements': movements, 'attacks': attacks}
