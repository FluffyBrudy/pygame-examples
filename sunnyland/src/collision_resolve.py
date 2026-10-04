from tilemap_parser import CollisionHit

from src.entities.base import Character
from src.objects.base import Item


def resolve_collision(collision_hit: CollisionHit):
    obj_a = collision_hit.object_a
    obj_b = collision_hit.object_b
    if isinstance(obj_a, Character) and isinstance(obj_b, Item):
        obj_b.on_collision()
    elif isinstance(obj_b, Character) and isinstance(obj_a, Item):
        obj_a.on_collision()
