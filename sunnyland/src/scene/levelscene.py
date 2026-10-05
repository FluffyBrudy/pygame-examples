from pathlib import Path
from typing import cast, override

import pygame
from pygkit import Signal
from tilemap_parser import (
    Camera,
    CollisionRunner,
    ICollidable,
    ObjectCollisionManager,
    PhysicsWorld,
    TileLayerRenderer,
    get_shape_aabb,
    load_map,
)
from tilemap_parser.runtime.collision.shapes import rect_vs_rect

from src.collision_resolve import resolve_collision
from src.entities.base import Character
from src.entities.enemies import Eagle, Frog, Opossum
from src.entities.foxy import Foxy
from src.loader import LevelData, SharedData
from src.objects.base import Item
from src.scene.base import Scene


class LevelScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    def enter(self):
        pass

    def exit(self):
        self._disconnect_signals(getattr(self, "foxy", None))
        for obj in getattr(self, "objct_container", []):
            self._disconnect_signals(obj)
        for fx in getattr(self, "fx_container", []):
            self._disconnect_signals(fx)
        self.soundmanager.stop_all()

    @staticmethod
    def _disconnect_signals(obj: object | None) -> None:
        if obj is None:
            return
        for name in ("sig_jumped", "sig_landed", "sig_hurt", "sig_died", "sig_collected"):
            sig = obj.__dict__.get(name) if hasattr(obj, "__dict__") else None
            if sig is not None:
                sig.disconnect_all()

    def load(self, **kwargs):
        level_path = kwargs.get("level_path", None)
        if not isinstance(level_path, Path):
            raise TypeError("Expected map path but received incompatible type")
        vw, vh = pygame.display.get_surface().size  # pyright: ignore

        mapdata = load_map(level_path)
        SharedData().preload(mapdata.render_scale)
        LevelData().preload(mapdata)

        self.physics_world = PhysicsWorld.from_map(
            mapdata,
            SharedData().tileset_collision["default"],
            collision_tileset="tileset",
            exclude_layers={"trees", "propsTile"},
        )
        self.collision_runner = CollisionRunner.from_world(self.physics_world)
        self.tilelayer_renderer = TileLayerRenderer(mapdata)
        self.background = LevelData().backgrounds
        self.level_completion_area = LevelData().level_completion_node

        Character.collision_runner = self.collision_runner
        Character.solid_tile_at = self.solid_tile_at
        Character.out_of_bound = self.out_of_bound

        x, y = LevelData().foxy_spwn_point
        self.foxy = Foxy(x, y)
        self._connect_foxy(self.foxy)

        self.camera = Camera(vw, vh)
        self.camera.follow(self.foxy)
        self.camera.set_bounds_from_map(mapdata)

        self.object_collision_manager = ObjectCollisionManager()
        self.objct_container: list[Character | Item] = []
        self.fx_container: list[Item] = []
        self.object_collision_manager.add_object(self.foxy)

        for k in LevelData().entity_spawn_points:
            points = LevelData().entity_spawn_points[k]
            for point in points:
                if k == "gem" or k == "cherry":
                    gem = Item(point[0], point[1], f"{k}.collision", f"{k}.anim")
                    self._connect_object(gem)
                    self.object_collision_manager.add_object(gem)
                    self.objct_container.append(gem)
                    continue

                enemy = None
                if k == "eagle":
                    enemy = Eagle(point[0], point[1])
                elif k == "opossum":
                    enemy = Opossum(point[0], point[1])
                elif k == "frog":
                    enemy = Frog(point[0], point[1])
                if enemy is not None:
                    self._connect_object(enemy)
                    self.objct_container.append(enemy)
                    self.object_collision_manager.add_object(enemy)

        self.soundmanager = SharedData().soundmanager
        self.soundmanager.play("arcade", "main")

    def _connect_foxy(self, foxy: Foxy) -> None:
        foxy.sig_jumped.connect(self._on_foxy_jump)
        foxy.sig_landed.connect(self._on_foxy_land)
        foxy.sig_hurt.connect(self._on_foxy_hurt)

    def _connect_object(self, obj: Character | Item) -> None:
        if isinstance(obj, Character):
            obj.sig_hurt.connect(self._on_entity_hurt)
            obj.sig_died.connect(self._on_entity_died)
        if isinstance(obj, Item):
            obj.sig_collected.connect(self._on_item_collected)
            obj.sig_collected.connect(lambda _: self.soundmanager.play("pickup"))

    def _on_foxy_hurt(self, foxy: Foxy, **kwargs):
        print(kwargs)
        foxy.vy -= 400
        if kwargs.get("normal_x"):
            foxy.vx = -kwargs["normal_x"] * self.collision_runner.horizontal_speed

    def _on_foxy_jump(self, foxy: Foxy) -> None:
        pass

    def _on_foxy_land(self, foxy: Foxy) -> None:
        pass

    def _on_entity_hurt(self, entity: Character, **kwargs) -> None:
        if isinstance(entity, Eagle):
            self._spawn_fx(entity.x, entity.y, "enemy-death.anim")

    def _on_entity_died(self, entity: Character) -> None:
        self._spawn_fx(entity.x, entity.y, "enemy-death.anim")
        if isinstance(entity, Eagle):
            self.soundmanager.play("bird_death", "sfx")

    def _on_item_collected(self, item: Item) -> None:
        _, t, _, b = get_shape_aabb(item.x, item.y, item.collision_shape)
        h = b - t
        self._spawn_fx(item.x, item.y - h, "item-feedback.anim")

    def _spawn_fx(self, x: float, y: float, anim_stem: str) -> None:
        fx = Item(x, y, "gem.collision", anim_stem, collidable=False)
        self.fx_container.append(fx)

    def can_transition(self):
        return self.level_completion_area.contains_point((self.foxy.x, self.foxy.y))

    def out_of_bound(self, obj: ICollidable):
        ox, oy = self.camera.offset
        vw, vh = self.camera.viewport_w, self.camera.viewport_h
        _, t, _, b = get_shape_aabb(obj.x, obj.y, obj.collision_shape)
        h = b - t
        return not (ox <= obj.x <= ox + vw and oy <= obj.y + h <= oy + vh)

    def solid_tile_at(self, sprite: ICollidable, direction: float = 0.0, upward: bool = False):
        l, t, r, b = get_shape_aabb(sprite.x, sprite.y, sprite.collision_shape)
        cx = (l + r) * 0.5
        if upward:
            probe_x, probe_y = cx, t - 2
        elif direction != 0:
            probe_x = (l - 2) if direction < 0 else (r + 2)
            probe_y = b + 2
        else:
            probe_x, probe_y = cx, b + 2
        tile_x, tile_y = self.collision_runner.get_tile_at(probe_x, probe_y)
        return self.physics_world.cell_has_collision((tile_x, tile_y))

    def update(self, dt: float):
        self.foxy.update(dt)
        self.camera.update(dt)
        for i in range(len(self.objct_container) - 1, -1, -1):
            obj = self.objct_container[i]
            obj.update(dt)
            if obj.can_kill():
                self.object_collision_manager.remove_object(obj)
                self._disconnect_signals(obj)
                del self.objct_container[i]

        for i in range(len(self.fx_container) - 1, -1, -1):
            fx = self.fx_container[i]
            fx.update(dt)
            if fx.animation.finished:
                self._disconnect_signals(fx)
                del self.fx_container[i]

        for hit in self.object_collision_manager.check_all_collisions():
            resolve_collision(hit)

    @override
    def render(self, screen: pygame.Surface):  # pyright: ignore
        cam_offset = self.camera.offset
        for background in self.background:
            screen.blit(background, (0, 0))
        self.tilelayer_renderer.render(screen, cam_offset)
        self.foxy.render(screen, cam_offset)
        for obj in self.objct_container:
            obj.render(screen, cam_offset)
        for fx in self.fx_container:
            fx.render(screen, cam_offset)
