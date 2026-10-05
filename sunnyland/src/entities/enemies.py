from random import choice, random

import pygame
from tilemap_parser import get_shape_aabb

from src.entities.base import Character


class Enemy(Character):
    def __init__(
        self,
        animation_stem: str,
        collision_stem: str,
        state: str,
        x: float,
        y: float,
    ) -> None:
        super().__init__(animation_stem, collision_stem, state, x, y, 0, 0)

    def can_kill(self):
        return self.is_dead

    def update(self, dt: float):
        return super().update(dt)

    def render(self, surface: pygame.Surface, offset: tuple[float, float]):
        frame = self.prepare_render()
        if frame is not None:
            surface.blit(frame, (self.x - offset[0], self.y - offset[1]))


class Eagle(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("eagle.anim", "eagle.collision", "attack", x, y)
        self.vy = choice([-100, 100, -150, 150])
        self.displacement = 0
        self.max_displacement = 300

    def get_state(self) -> str:
        return "attack"

    def update(self, dt: float):
        if self.solid_tile_at(self, 0, self.vy < 0) or self.displacement <= 0:
            self.vy *= -1
            self.displacement = self.max_displacement
        self.displacement -= dt * 100
        self.collision_runner.move_grounded(self, None, None, dt, velocity=(0, self.vy))
        return super().update(dt)


class Opossum(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("opossum.anim", "opossum.collision", "roam", x, y)
        self.speed = choice([100, 150])
        self.direction = choice([1, -1])
        self.vx = self.direction * self.speed

    def get_state(self) -> str:
        return "roam"

    def update(self, dt: float):
        self.flipped = self.direction < 0

        res = self.collision_runner.move_grounded(self, None, None, dt)
        hit_wall_x = res.hit_wall_x
        no_tile_ahead = not self.solid_tile_at(self, self.direction, False)
        if self.on_ground and (hit_wall_x or no_tile_ahead):
            self.direction *= -1

        self.vx = self.direction * self.speed
        super().update(dt)


class Frog(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("frog.anim", "frog.collision", "idle", x, y)
        self.direction = choice([1, -1])
        self.speed = choice([100, 150])
        self.jumping = self.speed

    def get_state(self) -> str:
        if abs(self.vx) > 0:
            return "jump"
        return "idle"

    def update(self, dt: float):
        self.collision_runner.move_grounded(self, None, None, dt)

        self.flipped = self.vx < 0
        if self.jumping > 0:
            self.jumping = max(self.jumping - 1, 0)
            self.vx = self.direction * self.speed
        elif random() < 0.01:
            self.jumping = choice([100, 150])
            self.direction *= -1
        else:
            self.vx = 0
        return super().update(dt)
