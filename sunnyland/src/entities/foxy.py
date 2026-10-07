from typing import Callable

import pygame
from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_UP
from pygame.rect import Rect

from src.entities.base import Character
from src.utils.index import emit_callbacks, move_towards


class Foxy(Character):
    CLIMB_SPEED = 100.0
    PARK_FEET_BELOW_TOP = 17.0

    def __init__(self, x: float, y: float) -> None:
        super().__init__("foxy.anim", "foxy.collision", "idle", x, y, 1, 10)
        self.jump_pressed = False
        self.roll_pressed = False
        self.just_jumped = False
        self.just_landed = False
        self.climbing_stair = False
        self.ground_angle = None
        self.direction = 1
        self.on_jumped: list[Callable] = []
        self.on_landed: list[Callable] = []
        self.input_keys = {k: False for k in [K_LEFT, K_RIGHT, K_UP, K_DOWN]}

    def get_state(self) -> str:
        if self.climbing_stair:
            return "climb"
        if self.hit_cd != 0:
            return "hurt"
        if self.roll_pressed or (self.ground_angle and int(self.ground_angle) != 0):
            return "roll"
        if self.vy < 0:
            return "jump"
        if (self.vy) > 0.01:
            return "fall"
        if abs(self.vx) > 0.01:
            return "run"
        return "idle"

    def _get_anim_time_scale(self):
        val = 1
        if self.climbing_stair:
            input_x = self.input_keys[pygame.K_RIGHT] - self.input_keys[pygame.K_LEFT]
            if not (self.input_keys[pygame.K_UP] or self.input_keys[pygame.K_DOWN] or input_x != 0):
                val = 0
        return val

    def _update_movement(self, input_x: int, speed_scale: float, dt: float):
        was_on_ground = self.on_ground
        if not was_on_ground:
            t = 0 if self.climbing_stair else 1
            self.vy = move_towards(self.vy, self.vy + self.collision_runner.gravity * t, dt * 800)
        elif self.jump_pressed:
            self.vy = -400

        if self.climbing_stair:
            dy = self.CLIMB_SPEED * dt
            if self.input_keys[pygame.K_UP]:
                self.y -= dy
            elif self.input_keys[pygame.K_DOWN]:
                self.y += dy

        self.vx = move_towards(self.vx, input_x * self.collision_runner.horizontal_speed * speed_scale, dt * 450)
        res = self.collision_runner.move_platformer_with_slide(self, None, None, dt, velocity=(self.vx, self.vy))
        self.ground_angle = res.ground_angle

    def get_movement(self):
        flat_ground_roll = (self.ground_angle is None) or (int(self.ground_angle) == 0)
        input_horizontal = self.input_keys[pygame.K_RIGHT] - self.input_keys[pygame.K_LEFT]
        speed_scale = 1
        if self.current_state == "roll":
            if flat_ground_roll:
                speed_scale = 2
                input_horizontal = self.direction
            elif (input_horizontal * self.ground_angle) <= 0:  # pyright: ignore
                input_horizontal = -1 if self.ground_angle > 0 else 1  # pyright: ignore
                speed_scale = 1.5
            else:
                speed_scale = 0.8
        return speed_scale, input_horizontal

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        for k in self.input_keys:
            self.input_keys[k] = keys[k]

        pre_input_x = self.input_keys[pygame.K_RIGHT] - self.input_keys[pygame.K_LEFT]
        if pre_input_x != 0:
            self.direction = pre_input_x

        speed_scale, input_x = self.get_movement()
        was_on_ground = self.on_ground

        self.flipped = self.direction == -1
        self.jump_pressed = keys[pygame.K_UP]
        self.roll_pressed = keys[pygame.K_SPACE]
        self._update_movement(input_x, speed_scale, dt)
        self.just_jumped = was_on_ground and self.vy < 0
        self.just_landed = not was_on_ground and self.on_ground

        if self.just_jumped:
            emit_callbacks(self.on_jumped, self)
        elif self.just_landed:
            emit_callbacks(self.on_landed, self)

        return super().update(dt * self._get_anim_time_scale())

    def render(self, surface: pygame.Surface, offset: tuple[float, float]):
        frame = self.prepare_render()
        if frame is not None:
            surface.blit(frame, (self.x - offset[0], self.y - offset[1]))
