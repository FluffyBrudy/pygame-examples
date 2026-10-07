from pygame import Surface
from tilemap_parser import AnimationPlayer, ICollidable

from src.loader import SharedData
from src.utils.index import emit_callbacks


class Item(ICollidable):
    def __init__(
        self,
        x: float,
        y: float,
        collision_stem: str,
        animation_set_stem: str,
        collidable=True,
    ) -> None:
        collision_data = SharedData().character_collision[collision_stem]
        animation_set = SharedData().state_animations[animation_set_stem]
        self.x = x
        self.y = y
        self.collision_shape = collision_data.shape
        self.collision_layer = collision_data.collision_layer if collidable else 0
        self.collision_mask = collision_data.collision_mask if collidable else 0
        self.animation = AnimationPlayer(animation_set, next(iter(animation_set.library.animations)))
        self.is_dead = False
        self.on_collected: list = []

    def update(self, dt: float):
        self.animation.update(dt * 1000)

    def render(self, surface: Surface, offset: tuple[float, float]):
        frame = self.animation.get_current_image()
        if frame is None:
            return
        surface.blit(frame, (self.x - offset[0], self.y - offset[1]))

    def on_collision(self, full: bool = False):
        if self.is_dead:
            return
        self.is_dead = True
        emit_callbacks(self.on_collected, self)

    def can_kill(self):
        return self.is_dead
