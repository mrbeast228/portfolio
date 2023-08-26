import os
import pygame

from base_classes import Cell


class GlobalVars:
    FPS = 240
    CELL_SIZE = 50
    WIDTH = 8 * (CELL_SIZE - 1)
    HEIGHT = WIDTH

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    BOARD_BASE = [(101, 167, 88, 255), (225, 225, 225, 255)]
    MOVABLE = (219, 84, 84, 155)
    ATTACKABLE = (214, 24, 24, 206)

    game_folder = os.path.dirname(__file__)
    img_folder = os.path.join(game_folder, 'img')
    scale_factor_x = 1
    scale_factor_y = 1

    # set global scale factor for entire window
    def setScaleFactor(self, scale_factor_x, scale_factor_y):
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y


class CellSprite(pygame.sprite.Sprite):
    def __init__(self, globalVars, screen, name='Empty_empty', image='P_black.png', x=0, y=0, color=None):
        # init variables
        self.origin_h = 0
        self.origin_w = 0
        self.color = None
        self.image = None

        # init sprite
        pygame.sprite.Sprite.__init__(self)

        # set sprite parameters
        self.name = name
        self.x = x
        self.y = y

        # transfer sub global vars
        self.globalVars = globalVars
        self.screen = screen

        # init image
        pathToImage = os.path.join(self.globalVars.img_folder, image)
        if not os.path.exists(pathToImage):
            pathToImage = os.path.join(self.globalVars.img_folder, 'P_black.png')
        self.raw_image = pygame.image.load(pathToImage)
        self.bare_image = None

        # create surface for image and scale it
        self.setColorLoadSprite(color)

        # init rect
        self.rect = self.image.get_rect()

        # init origin size
        self.origin_w = self.rect.width
        self.origin_h = self.rect.height

    # This function is useful for
    # 1. changing color of sprite
    # 2. (re)loading image to sprite
    # 3. scaling sprite
    def setColorLoadSprite(self, color=None):
        # check color
        if not color:
            color = self.globalVars.GREEN

        # set color
        self.color = color
        self.image = pygame.Surface((self.globalVars.CELL_SIZE * self.globalVars.scale_factor_x,
                                     self.globalVars.CELL_SIZE * self.globalVars.scale_factor_y),
                                    pygame.SRCALPHA)
        self.image.fill(self.color)

        # scale raw image to bare image
        if 'empty' not in self.name:
            self.bare_image = pygame.transform.scale(self.raw_image,
                                            (self.globalVars.CELL_SIZE * self.globalVars.scale_factor_x,
                                             self.globalVars.CELL_SIZE * self.globalVars.scale_factor_y))
            self.image.blit(self.bare_image, (0, 0))

        # reload rectangle
        self.rect = self.image.get_rect()

    # redraw sprite
    def update(self):
        self.rect.center = (self.x * self.globalVars.scale_factor_x, self.y * self.globalVars.scale_factor_y)


class CellFrontObject(CellSprite):
    def __init__(self, globalVars, screen, x=0, y=0, color=None, backend=None):
        # init backend
        self.backend = backend
        self.CellBackendObject = self.backend.whoOccupies(Cell(x, y))

        # init sprite
        name = self.CellBackendObject.createText()
        image = f"{name}.png"
        super().__init__(globalVars, screen, name, image, 0, 0, color)
        self.setSpriteCoords(x, y)

    # move sprite to coords (in cell mode)
    def setSpriteCoords(self, x, y):
        self.x = (x + 0.5) * self.globalVars.CELL_SIZE - x - 1
        self.y = (y + 0.5) * self.globalVars.CELL_SIZE - y - 1
