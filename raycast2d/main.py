from math import cos, pi, sin
from typing import Tuple
import pygame

from map import Map
from caster import Body
from settings import FOV, NUM_RAYS, SCREEN_HEIGHT, SCREEN_WIDTH, STEP_ANGLE, TILE_SIZE

class Raycast:
    _game_loop = True

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.map = Map()

        caster_pos_y = int(TILE_SIZE * 7 + TILE_SIZE * 0.5)
        self.caster = Body(SCREEN_WIDTH // 2,  caster_pos_y, 5, pi / 2)

    @staticmethod
    def cast_ray(start_pos: pygame.Vector2, angle: float, mapobj: Map):
        step = 2
        pos = start_pos
        direction = pygame.Vector2(cos(angle), sin(angle))
        while not mapobj.is_wall(*pos):
            pos += direction * step
        return pos

    def draw_line(self, end_pos: pygame.Vector2):
        pos = int(end_pos.x), int(end_pos.y)
        pygame.draw.line(self.screen, "red", self.caster.pos, pos, 3)

    def cast_rays(self):
        pos = self.caster.pos.copy()
        angle = self.caster.angle - FOV / 2
        for i in range(NUM_RAYS):
            ray_angle = angle + i * STEP_ANGLE
            ray_pos = self.cast_ray(self.caster.pos.copy(), ray_angle, self.map)
            self.draw_line(ray_pos)


    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game_loop = False

    def update(self):
        self.caster.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.map.render(self.screen)
        self.caster.render(self.screen)
        self.cast_rays()
        pygame.display.update((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def run(self):
        while self._game_loop:
            self.handle_event()
            self.update()
            self.render()
        pygame.quit()

if __name__ == "__main__":
    raycast = Raycast()
    raycast.run()
