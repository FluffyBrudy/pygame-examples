from pygame import Surface

from raycast2d.settings import NCOLS, NROWS


class Map:
    def __init__(self) -> None:
        # static corresponding to settings.NROWS and settings.NCOLS

        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,0,1,0,1,1,0,1],
            [1,0,1,0,0,0,0,1,0,1,0,0,1,0,1],
            [1,0,1,1,1,1,0,1,0,1,1,0,1,0,1],
            [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,1,0,1,1,1,0,1,1,1,0,1,1],
            [1,0,0,1,0,0,0,1,0,0,0,1,0,0,1],
            [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]

    def render(self, screen: Surface):
        grid = self.grid
        for row in range(NROWS):
            for col in range(NCOLS):
                if grid[row][col]
