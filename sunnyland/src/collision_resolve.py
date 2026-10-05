from tilemap_parser import CollisionHit, get_shape_aabb

from src.entities.base import Character
from src.entities.enemies import Eagle, Enemy
from src.objects.base import Item


def resolve_collision(collision_hit: CollisionHit):
    obj_a = collision_hit.object_a
    obj_b = collision_hit.object_b

    if isinstance(obj_a, Character) and isinstance(obj_b, Item):
        obj_b.on_collision()
    elif isinstance(obj_b, Character) and isinstance(obj_a, Item):
        obj_a.on_collision()

    elif isinstance(obj_a, Character) and isinstance(obj_b, Enemy):
        lb, tb, rb, bb = get_shape_aabb(obj_b.x, obj_b.y, obj_b.collision_shape)
        la, ta, ra, ba = get_shape_aabb(obj_a.x, obj_a.y, obj_a.collision_shape)
        if ba <= bb and obj_a.vy > 0 and obj_a.can_hit():
            obj_b.on_collision()
            obj_a.vy = -400
        elif obj_a.can_hit():
            obj_a.on_collision(full=False, normal_x=collision_hit.normal[0])
    elif isinstance(obj_b, Character) and isinstance(obj_a, Enemy):
        lb, tb, rb, bb = get_shape_aabb(obj_b.x, obj_b.y, obj_b.collision_shape)
        la, ta, ra, ba = get_shape_aabb(obj_a.x, obj_a.y, obj_a.collision_shape)
        if ba <= bb and obj_a.vy > 0 and obj_b.can_hit():
            obj_a.on_collision()
            obj_b.vy = -400
        elif obj_b.can_hit():
            obj_b.on_collision(full=False, normal_x=collision_hit.normal[0])
