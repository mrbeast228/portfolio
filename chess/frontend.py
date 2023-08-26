import pygame
from tkinter import *

from backend import Backend, King
from cells import GlobalVars, CellFrontObject
from base_classes import Cell
from ai import AI


class Frontend:
    def __init__(self, title="Chess", playerColor=1):
        # init game backend
        self.backend = Backend()
        self.backend.playerColor = playerColor

        # init AI
        self.ai = AI(self.backend)

        # init our instance of global vars
        self.globalVars = GlobalVars()

        # init the game and create screen
        pygame.init()
        self.screen = pygame.display.set_mode((self.globalVars.WIDTH, self.globalVars.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(title)

        # init clock
        self.clock = pygame.time.Clock()

        # init sprites
        self.all_sprites = pygame.sprite.Group()

    def loop(self):
        self.running = True
        selectedPiece = None

        while self.running:
            skipHumanMove = False

            # check for game end
            if self.backend.gameState:
                result = 'Game ended with '
                if self.backend.gameState == 1:
                    result += 'white victory'
                elif self.backend.gameState == -1:
                    result += 'black victory'
                else:
                    result += 'draw'
                result += '! Press OK to exit game...'

                self.tkinterChoiceBox(prompt=result)
                self.running = False

            # play with AI
            if self.backend.currentMove != self.backend.playerColor:
                skipHumanMove = self.ai.makeMove()

            # give move to second gamer on AI error
            if not skipHumanMove:
                # handle events
                for event in pygame.event.get():
                    # handle closing window
                    if event.type == pygame.QUIT:
                        self.running = False
                        return

                    # handle resizing window
                    if event.type == pygame.VIDEORESIZE:
                        # update variables
                        self.globalVars.WIDTH = event.w
                        self.globalVars.HEIGHT = event.h

                        # rescale sprites
                        self.globalVars.scale_factor_x = self.globalVars.WIDTH / GlobalVars.WIDTH
                        self.globalVars.scale_factor_y = self.globalVars.HEIGHT / GlobalVars.HEIGHT
                        for test_cell in self.all_sprites:
                            test_cell.setColorLoadSprite(test_cell.color)

                    # handle mouse click
                    if event.type == pygame.MOUSEBUTTONUP:
                        # get mouse position
                        pos = pygame.mouse.get_pos()

                        # check for sprites to found which we clicked
                        for sprite in self.all_sprites:
                            if sprite.rect.collidepoint(pos):
                                # determine backend piece object by click
                                piece = sprite.CellBackendObject

                                if not selectedPiece:
                                    # piece should be selected
                                    if piece.color != self.backend.currentMove:
                                        break  # not your turn yet
                                    selectedPiece = piece

                                    # highlight piece we moving
                                    self.findCellFront(selectedPiece).setColorLoadSprite(self.globalVars.MOVABLE)
                                else:
                                    if selectedPiece.color != self.backend.currentMove:
                                        break  # not your turn yet

                                    # release of castling
                                    if selectedPiece.__class__ == King and abs(selectedPiece.x - piece.x) == 2 and selectedPiece.countOfMoves == 0:
                                        self.backend.releaseCastling(selectedPiece, piece)
                                    else: # we should move selected piece
                                        self.backend.action(selectedPiece, piece)

                                    # drop selected piece
                                    selectedPiece = None

                                    # redraw board after move
                                    self.renderBoard()
                                # check we can transform pawn
                                if self.backend.toTransform:
                                    # ask user for piece to transform
                                    piece = self.tkinterChoiceBox(choice=['Queen', 'Rook', 'Bishop', 'Knight'], prompt='Choose piece to transform pawn')

                                    # transform pawn
                                    self.backend.transformPawn(piece)

                                    # redraw board after transform
                                    self.renderBoard()

                                # exit from finding sprite we clicked
                                break

            # create background
            self.screen.fill(self.globalVars.BLUE)

            # redraw sprites
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)

            # after drawing everything, flip the display (double buffering)
            pygame.display.flip()

    @staticmethod
    def tkinterChoiceBox(prompt, choice=[]):
        # create prompt box
        root = Tk()

        # set font
        root.option_add("*Font", "Arial 12")

        # create label
        label = Label(root, text=prompt)
        label.grid(row=0, column=0)

        if choice:
            # create variable
            var = StringVar(root)
            var.set(choice[0])

            # create option menu
            option = OptionMenu(root, var, *choice)
            option.configure(justify='left')
            option.grid(row=1, column=0)

        # create OK button
        submit = Button(root, text='OK', command=root.destroy)
        submit.configure(justify='center')
        submit.grid(row=1, column=1)

        # wait until user choose piece
        root.mainloop()

        # return user choice
        return None if not choice else var.get()

    # add cell to the board using data from backend
    def addCell(self, x, y, color=None):
        if not color:
            color = self.globalVars.RED
        self.all_sprites.add(CellFrontObject(self.globalVars, self.screen, x, y,
                                       color=color, backend=self.backend))

    # find front cell by back cell
    def findCellFront(self, cell: Cell):
        for sprite in self.all_sprites:
            if sprite.CellBackendObject.x == cell.x and sprite.CellBackendObject.y == cell.y:
                return sprite
        return None

    # (re)draw board
    def renderBoard(self):
        self.all_sprites.empty()
        for x in range(8):
            for y in range(8):
                self.addCell(x, y, self.globalVars.BOARD_BASE[(x + y) % 2])
