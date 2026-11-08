"""Cheap value noise, seeded from a random.Random so a seed always gives the
same world."""

import math

from .colors import lerp


class Noise:
    def __init__(self, rng):
        self.table = [rng.random() for _ in range(1024)]

    def n1(self, x):
        i = math.floor(x)
        f = x - i
        f = f * f * (3 - 2 * f)
        t = self.table
        return t[i & 1023] * (1 - f) + t[(i + 1) & 1023] * f

    def n2(self, x, y):
        ix, iy = math.floor(x), math.floor(y)
        fx, fy = x - ix, y - iy
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        t = self.table

        def corner(a, b):
            return t[((a * 73856093) ^ (b * 19349663)) & 1023]

        return lerp(lerp(corner(ix, iy), corner(ix + 1, iy), fx),
                    lerp(corner(ix, iy + 1), corner(ix + 1, iy + 1), fx), fy)

    def fbm1(self, x, octaves=4):
        total = norm = 0.0
        amp = .5
        for _ in range(octaves):
            total += amp * self.n1(x)
            norm += amp
            x *= 2.02
            amp *= .5
        return total / norm

    def fbm2(self, x, y, octaves=4):
        total = norm = 0.0
        amp = .5
        for _ in range(octaves):
            total += amp * self.n2(x, y)
            norm += amp
            x *= 2.03
            y *= 2.03
            amp *= .5
        return total / norm
