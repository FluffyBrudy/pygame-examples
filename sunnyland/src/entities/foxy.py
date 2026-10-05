import pygame
from pygkit import Signal, signal

from src.entities.base import Character
from src.utils.index import move_towards


class Foxy(Character):
    sig_jumped: Signal = signal()  # pyright: ignore
    sig_landed: Signal = signal()  # pyright: ignore

    def __init__(
        self,
        x: float,
        y: float,
    ) -> None:
        super().__init__("foxy.anim", "foxy.collision", "idle", x, y, 1, 10)
        self.jump_pressed = False
        self.roll_pressed = False
        self.just_jumped = False
        self.just_landed = False
        self.ground_angle = None
        self.direction = 1

    def get_state(self) -> str:
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

    def update(self, dt: float):
        speed_scale = 1
        keys = pygame.key.get_pressed()
        flat_ground_roll = (self.ground_angle is None) or (int(self.ground_angle) == 0)

        input_x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        if input_x != 0:
            self.direction = input_x

        if self.current_state == "roll":
            if flat_ground_roll:
                speed_scale = 2
                input_x = self.direction
            elif input_x == 0:  # pyright: ignore
                input_x = -1 if self.ground_angle > 0 else 1
                speed_scale = 1.5
            else:
                speed_scale = 0.8

        self.flipped = self.direction == -1
        self.jump_pressed = keys[pygame.K_UP]
        self.roll_pressed = keys[pygame.K_SPACE]

        # -
        was_on_ground = self.on_ground

        if not was_on_ground:
            self.vy = move_towards(self.vy, self.vy + self.collision_runner.gravity, dt * 800)
        elif self.jump_pressed:
            self.vy = -400

        self.vx = move_towards(self.vx, input_x * self.collision_runner.horizontal_speed * speed_scale, dt * 450)
        res = self.collision_runner.move_platformer_with_slide(self, None, None, dt, velocity=(self.vx, self.vy))
        self.ground_angle = res.ground_angle
        # -

        self.just_jumped = was_on_ground and self.vy < 0
        self.just_landed = not was_on_ground and self.on_ground
        if self.just_jumped:
            self.sig_jumped.emit(self)
        elif self.just_landed:
            self.sig_landed.emit(self)

        return super().update(dt)

    def render(self, surface: pygame.Surface, offset: tuple[float, float]):
        frame = self.prepare_render()
        if frame is not None:
            surface.blit(frame, (self.x - offset[0], self.y - offset[1]))
