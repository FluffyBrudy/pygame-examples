def move_towards(src: float, dest: float, dx: float):
    abs_dx = abs(dx)
    if src < dest:
        return min(src + abs_dx, dest)
    return max(src - abs_dx, dest)
