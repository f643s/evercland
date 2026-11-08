"""Colour helpers. A colour is just an (r, g, b) tuple of floats, 0-255."""


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = clamp(t)
    return (c1[0] + (c2[0] - c1[0]) * t,
            c1[1] + (c2[1] - c1[1]) * t,
            c1[2] + (c2[2] - c1[2]) * t)


def scale(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


def tint(c, mult):
    """Multiply each channel by its own factor (used for the season shifts)."""
    return tuple(clamp(v * m, 0, 255) for v, m in zip(c, mult))


def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0))
    return t * t * (3 - 2 * t)


def gradient(stops, t):
    """stops is a list of (position, colour), positions going 0 -> 1."""
    t = clamp(t)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            return mix(c0, c1, (t - p0) / (p1 - p0) if p1 > p0 else 0)
    return stops[-1][1]
