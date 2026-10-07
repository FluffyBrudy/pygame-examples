from collections import defaultdict
from typing import Literal

import pygame
from pygame import Font
from pygame.rect import Rect
from pygame.surface import Surface
from pygkit.audio import SoundManager
from tilemap_parser import (
    AreaNode,
    CharacterCollision,
    SpriteAnimationSet,
    TilemapData,
    TilesetCollision,
    get_cached_character_collision,
    get_cached_tileset_collision,
)

from src.settings import PROJECT_PATH


class SharedData:
    __instance: "SharedData | None" = None
    __instantiated = False

    def __init__(self) -> None:
        if type(self).__instantiated:
            return
        type(self).__instantiated = True
        self.state_animations: dict[str, SpriteAnimationSet] = {}
        self.character_collision: dict[str, CharacterCollision] = {}
        self.tileset_collision: dict[str | Literal["default"], TilesetCollision] = {}
        self.images: dict[str, Surface] = {}
        self.fonts: dict[str, Font] = {}
        self.soundmanager = SoundManager()

    def preload(self, scale: float):
        self.fonts["default"] = pygame.Font(
            PROJECT_PATH / "assets/fonts/pixify_sans/PixelifySans-VariableFont_wght.ttf"
        )

        animations_path = PROJECT_PATH / "data" / "animations"
        character_collision_path = PROJECT_PATH / "data" / "character_collision"
        tileset_collision_path = PROJECT_PATH / "data/collision/tileset.collision.json"

        tileset_collision = get_cached_tileset_collision(tileset_collision_path)
        if tileset_collision is None:
            raise ValueError("No tileset collison found")

        self.tileset_collision = {"default": tileset_collision}

        for anim_path in animations_path.iterdir():
            if anim_path.stem.startswith("_"):
                continue
            self.state_animations[anim_path.stem] = SpriteAnimationSet.load(
                anim_path,
                render_scale=scale,
            )

        for collision_path in character_collision_path.iterdir():
            if collision_path.stem.startswith("_"):
                continue
            collision_data = get_cached_character_collision(collision_path, scale)
            if collision_data is None:
                raise ValueError("Unable to load character colision")
            self.character_collision[collision_path.stem] = collision_data

        self.__load_sounds()

    def __load_sounds(self):
        sound_path = PROJECT_PATH / "assets/SunnyLand Music/pack1"
        self.soundmanager.add_sound(sound_path / "arcade.ogg", "arcade", "main")
        self.soundmanager.add_sound(sound_path / "Retro PickUp 18.wav", "pickup", "sfx")
        self.soundmanager.add_sound(sound_path / "bird_death.ogg", "bird_death", "sfx")

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


class LevelData:
    __instance: "LevelData | None" = None
    __instantiated = False

    def __init__(self) -> None:
        if type(self).__instantiated:
            return
        type(self).__instantiated = True

    def preload(self, mapdata: TilemapData):
        self.backgrounds: list[Surface] = []
        self.background_layers: list[tuple[str, Surface]] = []
        self.foxy_spwn_point = (0, 0)
        self.entity_spawn_points: dict[str, list[tuple[float, float]]] = defaultdict(list)
        self.level_completion_node = next(node for node in mapdata.area_nodes if node.name == "level_completed")
        self.area_nodes: dict[str, list[AreaNode]] = defaultdict(list)

        scale = mapdata.render_scale

        for area_node in mapdata.area_nodes:
            self.area_nodes[area_node.name].append(area_node)

        for parsed_layer in mapdata.get_layers(layer_type="image"):
            surface = mapdata.get_placed_image_layer_surface(parsed_layer.name, render_scale=scale)
            if surface is None:
                continue
            self.backgrounds.append(surface)
            self.background_layers.append((parsed_layer.name, surface))

        for layer in mapdata.get_layers(layer_type="object"):
            for surf, x, y, oid in mapdata.get_object_surfaces(layer_id_or_name=layer.id, scaled=True):
                props = mapdata.parsed.tilesets[layer.objects[oid].ttype].properties
                if layer.name == "entities":
                    if props is None or props.get("name", None) is None:
                        continue
                    props_name = props["name"]
                    if props_name == "foxy":
                        self.foxy_spwn_point = (x, y)
                    self.entity_spawn_points[props_name].append((x, y))

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
