from abc import ABC, abstractmethod
from collections.abc import Callable

import pygame
from pygame import Surface
from tilemap_parser import AnimationPlayer, CollisionRunner, ICollidable, ICollidableSprite

from src.loader import SharedData
from src.utils.index import emit_callbacks


class Character(ABC, ICollidableSprite):
    """Note: priorize death animations when is_dead is true
    insted of overenginnering it feels much pragmatic and valid
    till synced"""

    collision_runner: "CollisionRunner"
    solid_tile_at: Callable[[ICollidable, float, bool], bool]
    out_of_bound: Callable[[ICollidable], bool]

    def __new__(cls, *args, **kwargs):
        if getattr(cls, "collision_runner", None) is None:
            raise ValueError("Collision runner is not attached")
        if getattr(cls, "solid_tile_at", None) is None:
            raise ValueError("Solid tile checker not implemented")
        if getattr(cls, "out_of_bound", None) is None:
            raise ValueError("Out of bound not implemented")

        return super().__new__(cls)

    def __init__(
        self,
        sprite_animation_set_stem: str,
        character_collision_stem: str,
        initial_state: str,
        x: float,
        y: float,
        max_hit_cd: float,
        max_hit_count: int,
    ) -> None:
        character_collision = SharedData().character_collision[character_collision_stem]
        sprite_animation_set = SharedData().state_animations[sprite_animation_set_stem]

        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.collision_shape = character_collision.shape
        self.collision_mask = character_collision.collision_mask
        self.collision_layer = character_collision.collision_layer

        self.flipped = False
        self.current_state = initial_state
        self.animations = {k: AnimationPlayer(sprite_animation_set, k) for k in sprite_animation_set.library.animations}
        self.animation_fps = {k: v.fps / 60.0 for k, v in sprite_animation_set.library.animations.items()}

        self.hit_count = 0
        self.max_hit_count = max_hit_count
        self.hit_cd = 0
        self.max_hit_cd = max_hit_cd
        self.is_dead = False

        self.on_hurt: list[Callable] = []
        self.on_died: list[Callable] = []

    @abstractmethod
    def get_state(self) -> str: ...
    @abstractmethod
    def render(self, surface: Surface, offset: tuple[float, float]): ...

    def can_kill(self):
        return self.is_dead and self.animations[self.current_state].finished

    def can_hit(self):
        return not self.is_dead and self.hit_cd == 0

    def manage_cd(self, dt: float):
        if self.hit_cd > 0:
            self.hit_cd = max(self.hit_cd - dt, 0)

    def on_collision(self, full: bool = False, **kwargs):
        if self.is_dead:
            return
        if full:
            self.hit_count = self.max_hit_count + 1
        else:
            self.hit_count += 1
            self.hit_cd = self.max_hit_cd

        if self.hit_count > self.max_hit_count and not self.is_dead:
            self.is_dead = True
            emit_callbacks(self.on_died, self)
        else:
            print(kwargs)
            emit_callbacks(self.on_hurt, self, **kwargs)

    def manage_state(self):
        next_state = self.get_state()
        if self.current_state != next_state:
            self.animations[next_state].reset()
            self.current_state = next_state

    def update(self, dt: float):
        self.manage_cd(dt)
        self.manage_state()
        self.animations[self.current_state].update(
            dt * 1000 * self.animation_fps[self.current_state],
        )

    def prepare_render(self):
        frame = self.animations[self.current_state].get_current_image()
        if frame is None:
            return
        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)
        return frame
