from math import cos, pi, sin
from typing import TYPE_CHECKING
from pygame import Surface, Vector2
import pygame

if TYPE_CHECKING:
    from map import Map


ANGULAR_SPEED = pi / 180.0
MOVE_SPEED = 1
LINE_LENGTH = 100
LINE_WIDTH = 3
BODY_COLOR = (100, 150, 100)

class Body:
    def __init__(self, x: int, y: int, r: int, start_angle: float = 0) -> None:
        self.r = r
        self.pos = Vector2(x, y)
        self.angle = start_angle
        self.direction = 0

    def _handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.angle -= ANGULAR_SPEED
        if keys[pygame.K_RIGHT]:
            self.angle += ANGULAR_SPEED

        if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            direction = (keys[pygame.K_UP]) * 2 - 1
            self.pos += Vector2(cos(self.angle), sin(self.angle)) * direction

    def update(self):
        self._handle_input()

    def render(self, screen: Surface):
        pygame.draw.circle(screen, BODY_COLOR, self.pos, self.r)


