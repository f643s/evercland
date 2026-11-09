"""All the colours in one place.

Everything is picked for a clear sunny day first. Time of day and season are
layered on top of that in scene.py.
"""

TIMES = ("dawn", "day", "dusk", "night")
SEASONS = ("spring", "summer", "autumn", "winter")

# sky gradient (top -> horizon) plus a few colours the rest of the scene borrows
SKY = {
    "day": dict(
        stops=[(0, (38, 98, 190)), (.6, (110, 175, 230)), (1, (200, 228, 245))],
        land=(70, 95, 130), sun=(255, 246, 215), glow=(255, 232, 170),
        water=(28, 78, 120), fg=(9, 22, 18)),
    "dawn": dict(
        stops=[(0, (52, 62, 130)), (.45, (170, 110, 160)),
               (.8, (250, 150, 130)), (1, (255, 208, 140))],
        land=(96, 70, 112), sun=(255, 238, 195), glow=(255, 172, 112),
        water=(60, 60, 110), fg=(18, 14, 28)),
    "dusk": dict(
        stops=[(0, (28, 30, 92)), (.4, (120, 60, 120)),
               (.75, (228, 92, 92)), (1, (255, 160, 80))],
        land=(70, 40, 92), sun=(255, 205, 145), glow=(255, 112, 70),
        water=(50, 30, 80), fg=(14, 8, 20)),
    "night": dict(
        stops=[(0, (3, 5, 18)), (.6, (14, 22, 52)), (1, (40, 56, 100))],
        land=(20, 28, 54), sun=(236, 238, 226), glow=(120, 150, 220),
        water=(8, 14, 34), fg=(2, 4, 8)),
}

# base colour of the forested hills (teal by day, purple-ish at dusk, nearly black at night)
FOREST = {
    "day": (50, 86, 86),
    "dawn": (74, 64, 100),
    "dusk": (62, 38, 80),
    "night": (12, 22, 40),
}

# how bright the world is, used to light the seasonal colours below
LIGHT = {"day": 1.0, "dawn": .85, "dusk": .7, "night": .3}

# What changes with the seasons.
#   forest    per-channel multiplier on the forest colour
#   leaves    colours of the broadleaf trees (winter has none, they're bare)
#   ground    (colour, strength) of the foreground ground
#   snow      how high up the mountains the snow starts (smaller = more snow)
#   cloud     cloud threshold, smaller = more clouds
#   haze      (colour, amount) the sky gets pushed towards
#   falling   what drifts through the air, if anything
#   broadleaf share of the forest that isn't conifers
#   birds     pick one of these for the flock size
SEASON = {
    "spring": dict(
        forest=(1.0, 1.2, .95),
        leaves=[(150, 210, 110), (120, 190, 90), (255, 170, 200)],
        ground=((70, 120, 60), .35),
        snow=.62, cloud=.54,
        haze=((200, 235, 255), .05),
        falling="petals", broadleaf=.35, birds=(2, 3, 4, 5)),
    "summer": dict(
        forest=(.95, 1.12, .85),
        leaves=[(60, 130, 60), (80, 150, 70), (50, 110, 60)],
        ground=((50, 100, 50), .35),
        snow=.78, cloud=.62,
        haze=((0, 0, 0), 0),
        falling=None, broadleaf=.35, birds=(0, 2, 3, 4)),
    "autumn": dict(
        forest=(1.1, 1.0, .8),
        leaves=[(220, 120, 40), (200, 70, 40), (235, 180, 50), (170, 60, 40)],
        ground=((120, 80, 40), .4),
        snow=.66, cloud=.52,
        haze=((255, 200, 140), .07),
        falling="leaves", broadleaf=.6, birds=(0, 3, 4, 6)),
    "winter": dict(
        forest=(.85, .95, 1.05),
        leaves=[],
        ground=((225, 235, 250), .7),
        snow=.34, cloud=.48,
        haze=((175, 190, 210), .2),
        falling="snow", broadleaf=.3, birds=(0, 0, 0, 2)),
}

# things that fall: how many (one per this many pixels), speed range in px/s,
# sideways drift in px/s and how much they sway
FALLING = {
    "snow": dict(per=320, speed=(2.5, 5.0), wind=.8, sway=1.5),
    "leaves": dict(per=1500, speed=(1.5, 3.0), wind=2.0, sway=2.5),
    "petals": dict(per=1600, speed=(1.5, 3.0), wind=1.2, sway=2.0),
}
