"""Little tree sprites.

They all draw straight into a grid (a list of rows of colours) and quietly
skip anything that lands outside of it. `side` is +1 or -1 and says which side
of the tree the sun is on, that half gets the light colour.
"""

from .colors import mix


def _put(grid, x, y, colour):
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = colour


def pine(grid, x, base, tall, dark, light, side, fat=.5, snow=None, trunk=0):
    """A spruce. `base` is the row of the lowest branches. If `snow` is given
    some of the tiers get dusted with it."""
    width = max(.9, tall * fat)
    tier = max(2, tall // 3)
    for r in range(tall):
        y = base - tall + 1 + r
        if not 0 <= y < len(grid):
            continue
        half = width * ((r + 1) / tall) ** .85
        if tall >= 6:
            half *= .8 + .2 * ((r % tier) / tier)
        dusted = snow is not None and (r % tier) < max(1, int(tier * .3))
        for xx in range(round(x - half), round(x + half) + 1):
            if 0 <= xx < len(grid[0]):
                sunny = (xx - x) * side >= 0
                c = light if sunny else dark
                if dusted:
                    c = mix(c, snow, .5 if sunny else .2)
                grid[y][xx] = c
    for y in range(base - trunk + 1, base + 1):
        _put(grid, round(x), y, dark)


def broadleaf(grid, x, base, tall, light, dark, side, trunk_colour):
    """A round-ish tree: short trunk and a blobby crown."""
    trunk = max(1, int(tall * .3))
    ry = max(1.0, (tall - trunk) / 2)
    rx = max(1.0, tall * .4)
    cy = base - trunk - ry
    for yy in range(int(cy - ry), int(cy + ry) + 1):
        for xx in range(round(x - rx), round(x + rx) + 1):
            if ((xx - x) / rx) ** 2 + ((yy - cy) / ry) ** 2 > 1:
                continue
            sunny = (xx - x) * side >= 0
            c = light if sunny else dark
            if sunny and yy < cy - ry * .3:
                c = mix(c, (255, 255, 255), .12)   # the top catches the most light
            _put(grid, xx, yy, c)
    for y in range(base - trunk + 1, base + 1):
        _put(grid, round(x), y, trunk_colour)


def bare(grid, x, base, tall, wood, snow=None):
    """Winter tree with no leaves, just a trunk and a couple of twigs."""
    x = round(x)
    height = max(2, int(tall * .85))
    for r in range(height):
        _put(grid, x, base - r, wood)
    top = base - height + 1
    if height >= 3:
        _put(grid, x - 1, top + 1, wood)
        _put(grid, x + 1, top + 1, wood)
    if snow is not None:
        _put(grid, x, top, snow)
