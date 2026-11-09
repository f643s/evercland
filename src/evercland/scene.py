"""The landscape itself.

Everything gets drawn into plain lists of (r, g, b) tuples, one tuple per
"pixel". A terminal cell holds two pixels (top and bottom half block) so the
picture is twice as tall as the terminal is in rows.

Scene() builds the parts that never move (sky, mountains, trees, ground) once.
Scene.frame(t) then adds the parts that do (clouds, water, birds, snow...) and
gives back a finished picture.
"""

import math
import random

from . import trees
from .colors import clamp, gradient, lerp, mix, scale, smoothstep, tint
from .noise import Noise
from .palette import FALLING, FOREST, LIGHT, SEASON, SKY

# where the sun sits, as a fraction of the way down to the horizon
SUN_HEIGHT = {"day": (.22, .40), "dawn": (.68, .82),
              "dusk": (.68, .82), "night": (.20, .45)}
# lower sun = longer shadows
SUN_ELEVATION = {"day": .9, "dawn": .22, "dusk": .22, "night": .55}

FOOTHILLS = 2

# How tall the forest band along the lake is. 1.0 is the tall version, smaller
# means a shorter forest and bigger-looking mountains.
FOREST_HEIGHT = .55


def moving_average(values, radius):
    sums = [0.0]
    for v in values:
        sums.append(sums[-1] + v)
    out = []
    for i in range(len(values)):
        lo, hi = max(0, i - radius), min(len(values), i + radius + 1)
        out.append((sums[hi] - sums[lo]) / (hi - lo))
    return out


def crossfade(a, b, k):
    """Blend two pictures of the same size. k=0 is all a, k=1 is all b."""
    return [[mix(p, q, k) for p, q in zip(ra, rb)] for ra, rb in zip(a, b)]


class Scene:
    def __init__(self, width, height, seed, time_of_day, season="summer", aspect=1.0):
        self.w, self.h = width, height
        self.seed = seed
        self.tod = time_of_day
        self.season = season
        self.aspect = aspect              # pixel height / pixel width
        self.night = time_of_day == "night"
        self.winter = season == "winter"

        self.rng = random.Random(seed)
        self.noise = Noise(self.rng)
        self.sea = SEASON[season]
        self.pal = self._make_palette()
        self.horizon = int(height * .70)
        self.haze = gradient(self.pal["stops"], 1)

        # I tuned everything on a ~110x64 canvas. These keep the noise and the
        # feature sizes about the same when the window is a different size.
        self.nx = 110 / max(width, 40)
        self.ny = 64 / max(height, 30)
        self.unit = clamp(height / 64, .5, 2.5)

        self.slant = clamp(.5 / SUN_ELEVATION[time_of_day], .4, 1.0)

        if self.night:
            self.cloud_light, self.cloud_shade = (95, 110, 160), (14, 20, 40)
        else:
            pal = self.pal
            self.cloud_light = mix(pal["glow"], (255, 255, 255), .55)
            self.cloud_shade = mix(gradient(pal["stops"], .45), pal["land"], .5)

        self._place_sun()
        self._build_sky()
        self._build_stars()
        self._build_land()
        self._build_foreground()
        self._scatter_life()

    # ------------------------------------------------------------------
    # small helpers

    def _make_palette(self):
        pal = dict(SKY[self.tod])
        colour, amount = self.sea["haze"]
        if amount:
            colour = scale(colour, LIGHT[self.tod])
            pal["stops"] = [(p, mix(c, colour, amount)) for p, c in pal["stops"]]
        return pal

    def _lit(self, colour):
        """Take a colour picked for a sunny day and light it for the current time."""
        k = LIGHT[self.tod]
        c = mix(scale(colour, k), self.pal["land"], (1 - k) * .45)
        if self.tod in ("dawn", "dusk"):
            c = mix(c, self.pal["glow"], .12)
        return c

    def _snow_colour(self):
        return self._lit((236, 242, 252))

    # ------------------------------------------------------------------
    # sky

    def _place_sun(self):
        lo, hi = SUN_HEIGHT[self.tod]
        self.sun_x = int(self.w * self.rng.uniform(.22, .78))
        self.sun_y = self.horizon * self.rng.uniform(lo, hi)
        self.sun_r = max(2.2, self.h * (.05 if self.night else .055))
        self.moon_phase = self.rng.choice([0, 0, .6, 1.1])    # full, gibbous, crescent

    def _build_sky(self):
        self.sky = [[self._sky_pixel(x, y) for x in range(self.w)]
                    for y in range(self.horizon)]

    def _sky_pixel(self, x, y):
        pal = self.pal
        r = self.sun_r
        c = gradient(pal["stops"], (y / self.horizon) ** 1.1)
        d = math.hypot(x - self.sun_x, (y - self.sun_y) * self.aspect)
        glow = math.exp(-(d / (r * (7 if self.night else 6))) ** 2)
        c = mix(c, pal["glow"], glow * (.35 if self.night else .55))
        c = mix(c, pal["sun"], math.exp(-(d / (r * 1.8)) ** 2) * .5)
        if self.night:
            c = self._milky_way(c, x, y)
        if d < r + 1:
            edge = clamp(r + .5 - d)
            if self.night:
                c = mix(c, self._moon_colour(x, y), edge * self._moon_lit(x, y))
            else:
                c = mix(c, pal["sun"], edge)
        return c

    def _milky_way(self, c, x, y):
        dist = abs(y - (self.horizon * .1 + x * .35)) / 1.06
        band = math.exp(-(dist / (self.h * .14)) ** 2)
        n = self.noise.fbm2(x * .08 * self.nx, y * .12 * self.ny + 5)
        return mix(c, (130, 140, 200), n * band * .38)

    def _moon_lit(self, x, y):
        if not self.moon_phase:
            return 1.0
        shadow_x = self.sun_x + self.moon_phase * self.sun_r * 1.3
        d = math.hypot(x - shadow_x, (y - self.sun_y) * self.aspect)
        return clamp(d - self.sun_r * 1.05 + .5)

    def _moon_colour(self, x, y):
        craters = self.noise.fbm2(x * .7, y * .7, 3)
        return mix(self.pal["sun"], (165, 172, 168), craters * .9)

    def _build_stars(self):
        self.stars = []
        if not self.night:
            return
        rng, hz = self.rng, self.horizon
        for _ in range(int(self.w * hz / 70)):
            x, y = rng.randrange(self.w), rng.randrange(int(hz * .95))
            if math.hypot(x - self.sun_x, (y - self.sun_y) * self.aspect) < self.sun_r * 2.2:
                continue
            bright = (rng.random() ** 3 * .9 + .1) * (1 - y / hz) ** .5
            self.stars.append((x, y, bright, rng.random()))

    # ------------------------------------------------------------------
    # mountains, foothills, far shore (all stored in self.land, sky rows only)

    def _build_land(self):
        w = self.w
        self.land = [[None] * w for _ in range(self.horizon)]
        # which way the light comes from at each column: towards the sun, fading
        # to nothing right underneath it so there's no hard seam
        self.light_dir = [clamp((self.sun_x - x) / (w * .18), -1, 1) for x in range(w)]
        skyline = self._build_ranges()
        self._build_foothills(skyline)
        self._build_far_shore()

    def _peak_height(self, x, freq, offset, amp):
        n = self.noise.fbm1(x * freq + offset, 5)
        n = clamp(.5 + (n - .5) * 2.2)        # more contrast = sharper peaks
        n = (1 - abs(2 * n - 1)) ** 1.6
        return amp * (.15 + .85 * n)

    def _build_ranges(self):
        """The snowy mountains. Returns the altitude of the skyline per column."""
        w, h, hz = self.w, self.h, self.horizon
        pal, haze, noise = self.pal, self.haze, self.noise
        count = 3 if h >= 44 else 2
        skyline = [0.0] * w
        win = max(2, int(w * .012))
        shadow = scale(pal["land"], .45)
        shadow = (shadow[0] * .9, shadow[1] * .95, shadow[2] * 1.15)

        for i in range(count):
            k = i / max(1, count - 1)         # 0 = farthest range, 1 = nearest
            amp = h * lerp(.55, .22, k)
            base = h * lerp(.04, .02, k)
            freq = lerp(.014, .035, k) * self.nx
            offset = self.rng.uniform(0, 900)
            body = scale(mix(haze, pal["land"], .25 + .5 * k), 1 - .15 * k)
            lit_c = mix(body, pal["glow"], .22)
            shade_c = mix(body, shadow, .55)

            heights = [self._peak_height(x, freq, offset, amp)
                       for x in range(-win, w + win)]

            # does this bit of slope face the sun?
            facing = []
            for x in range(w):
                slope = (heights[x + 2 * win] - heights[x]) / (2 * win)
                d = self.light_dir[x]
                facing.append(smoothstep(-.12, .12, -d * slope) * (.5 + .5 * abs(d)))

            for x in range(w):
                peak = heights[x + win]
                ridge = hz - base - peak
                skyline[x] = max(skyline[x], base + peak)
                for y in range(max(0, math.ceil(ridge)), hz):
                    depth = y - ridge
                    # shadow edges slant away from the sun as they go down the face
                    xs = x + self.light_dir[x] * depth * self.slant
                    lit = facing[min(w - 1, max(0, int(round(xs))))]
                    c = mix(shade_c, lit_c, lit)
                    rock = noise.fbm2(x * .25 * self.nx + offset, y * .5 * self.ny, 3)
                    c = scale(c, 1 + (rock - .5) * .14)
                    # mist pools at the bottom of every range
                    fog = clamp(1 - (hz - y) / (h * .30)) ** 1.3 * (.55 - .15 * k)
                    c = mix(c, haze, fog + (1 - k) * .04)
                    if peak / amp > self.sea["snow"]:
                        c = self._snow_cap(c, xs, depth, peak / amp, amp, lit, offset, k)
                    self.land[y][x] = c
        return skyline

    def _snow_cap(self, c, xs, depth, ratio, amp, lit, offset, k):
        cover = (ratio - self.sea["snow"]) * amp * .75 * (.6 + .8 * lit)
        ragged = (self.noise.fbm2(xs * .22 * self.nx + offset, depth * .16 * self.ny, 3)
                  - .5) * amp * .5
        if depth >= max(cover * .5, cover + ragged):
            return c
        snow = mix((150, 165, 205), (250, 252, 255), lit)
        if self.night:
            snow = mix(snow, self.pal["land"], .6)
        return mix(snow, self.haze, (1 - k) * .2)

    def _build_foothills(self, skyline):
        w, h, hz = self.w, self.h, self.horizon
        noise = self.noise
        # the forest follows the mountains a bit, but only a bit
        smoothed = moving_average(skyline, max(3, int(w * .04)))
        forest = tint(FOREST[self.tod], self.sea["forest"])

        for j in range(FOOTHILLS):            # 0 = far ridge, 1 = near ridge
            amp = h * (.07 - .025 * j) * FOREST_HEIGHT
            follow = (.09 - .045 * j) * FOREST_HEIGHT
            base = h * .02 * (1 - j) * FOREST_HEIGHT
            freq = (.018 + .012 * j) * self.nx
            offset = self.rng.uniform(0, 900)
            if j == 0:
                col = mix(forest, self.haze, .28)
            else:
                col = mix(forest, self.pal["fg"], .42)

            crest = []
            for x in range(w):
                n = noise.fbm1(x * freq + offset, 5)
                height = (amp * (.25 + .75 * n)
                          + self.unit * .7 * FOREST_HEIGHT * noise.n1(x * 1.1 * self.nx + offset)
                          + follow * smoothed[x])
                crest.append(hz - base - height)

            deepest = max(2.0, max(hz - y for y in crest))
            self._paint_hill(j, crest, col, deepest)
            self._plant_forest(j, crest, col, deepest)

    def _paint_hill(self, j, crest, col, deepest):
        """The ground under the trees: dark at the bottom, misty up top."""
        w, hz = self.w, self.horizon
        noise, pal = self.noise, self.pal
        span = max(2.0, deepest * .9)
        for x in range(w):
            sun = math.exp(-((x - self.sun_x) / (w * .4)) ** 2)
            for y in range(max(0, math.ceil(crest[x])), hz):
                below = y - crest[x]
                t = clamp(below / span)
                c = mix(scale(col, 1.12), scale(col, .82), smoothstep(0, 1, t))
                rim = math.exp(-below / max(1.5, span * .22))
                c = mix(c, pal["glow"], .14 * sun * rim)
                if j == 0:
                    c = mix(c, self.haze, .22 * smoothstep(.5, 1, t))
                grain = noise.n2(x * 1.6 * self.nx, y * .45 * self.ny) - .5
                self.land[y][x] = scale(c, 1 + grain * .10)

    def _plant_forest(self, j, crest, col, deepest):
        """Rows of trees down the whole ridge. Near the top of high ridges the
        trees thin out and get smaller, like a real tree line."""
        w, h, hz = self.w, self.h, self.horizon
        rng = random.Random(self.seed * 31 + j)
        haze, glow = self.haze, self.pal["glow"]
        broad = self.sea["broadleaf"]
        leaves = [self._lit(c) for c in self.sea["leaves"]]
        snow = self._snow_colour() if self.winter else None

        tree_h = self.unit * (1.8 if j == 0 else 2.8) * (.5 + .5 * FOREST_HEIGHT)
        gap = max(2.0, tree_h * .6)
        rows = max(1, int(deepest * .9 / gap))

        for row in range(rows):
            d = row * gap
            shade = 1 - .25 * d / (deepest + 1)          # lower rows a bit darker
            mist = .22 * smoothstep(.5, 1, d / deepest) if j == 0 else 0
            x = -rng.random() * gap
            while x < w:
                here = x
                x += gap * rng.uniform(.8, 1.4)
                xi = int(clamp(round(here), 0, w - 1))
                y = crest[xi] + d
                if y > hz - 1:
                    continue
                high = clamp((hz - crest[xi]) / (h * .30))
                if row < 2 and rng.random() < .5 * high:
                    continue
                altitude = hz - y
                tall = max(2, int(tree_h * rng.uniform(.85, 1.2)
                                  * (1 - .4 * clamp(altitude / (h * .30)))))
                base = int(round(y + tall * (.35 if row == 0 else .6)))
                v = shade * rng.uniform(.92, 1.08)
                side = 1 if self.light_dir[xi] >= 0 else -1
                sun = math.exp(-((xi - self.sun_x) / (w * .4)) ** 2)

                if rng.random() < broad * (1 - .6 * high):
                    if self.winter:
                        wood = mix(scale(col, .55 * v), haze, mist)
                        trees.bare(self.land, here, base, tall, wood, snow)
                    else:
                        leaf = mix(rng.choice(leaves), col, .15)   # calm the colour down a bit
                        light = mix(scale(leaf, v), haze, mist)
                        trees.broadleaf(self.land, here, base, int(tall * 1.3) + 1, light,
                                        scale(light, .7), side, scale(col, .5 * v))
                else:
                    dark = mix(scale(col, .72 * v), haze, mist)
                    glow_amt = (.06 + .10 * sun) * (.45 if self.night else 1)
                    light = mix(mix(scale(col, v), glow, glow_amt), haze, mist)
                    trees.pine(self.land, here, base, tall, dark, light, side, snow=snow)

    def _build_far_shore(self):
        """Dark strip of pines on the other side of the lake."""
        w, hz = self.w, self.horizon
        pal = self.pal
        col = tint(mix(pal["land"], pal["fg"], .62), self.sea["forest"])
        for x in range(w):
            for y in range(hz - 2, hz):
                self.land[y][x] = col
        rng = random.Random(self.seed * 17 + 5)
        x = 0.0
        while x < w:
            xi = int(min(w - 1, x))
            clump = self.noise.fbm1(xi * .3 * self.nx + 40, 3)
            tall = max(2, int((1.2 + 2.2 * clump) * self.unit * rng.uniform(.8, 1.2)))
            side = 1 if self.light_dir[xi] >= 0 else -1
            trees.pine(self.land, x, hz - 1, tall, scale(col, .8), col, side)
            x += max(1.0, self.unit * 1.2 * rng.uniform(.7, 1.3))

    # ------------------------------------------------------------------
    # foreground: the shore and the big trees at the sides

    def _ground_height(self, x):
        u = x / self.w
        left = max(0, 1 - u / .30) ** 2 * self.h * .20
        right = max(0, (u - .70) / .30) ** 2 * self.h * .17
        return 2 + 3 * self.noise.n1(x * .08) + left + right

    def _build_foreground(self):
        w, h, hz = self.w, self.h, self.horizon
        noise, haze, fg = self.noise, self.haze, self.pal["fg"]
        colour, strength = self.sea["ground"]
        ground = self._lit(colour)
        body = mix(fg, ground, strength)
        top = mix(mix(body, ground, .85 if self.winter else .4), haze, .12)

        # flowers in spring, fallen leaves in autumn
        if self.season == "spring":
            sprinkles = [self._lit(c) for c in [(255, 150, 200), (255, 235, 110), (235, 235, 255)]]
        elif self.season == "autumn":
            sprinkles = [self._lit(c) for c in self.sea["leaves"]]
        else:
            sprinkles = []

        rng = random.Random(self.seed * 13 + 7)
        self.fg = [[None] * w for _ in range(h)]
        tops = [int(h - self._ground_height(x)) for x in range(w)]
        span = max(3, h * .07)

        for x in range(w):
            t = tops[x]
            for y in range(max(t, hz), h):
                d = clamp((y - t) / span)
                grain = (noise.n2(x * .5 * self.nx, y * .8 * self.ny) - .5) * .25
                c = mix(mix(top, haze, .04 + grain * .3), body, d)
                if sprinkles and y - t < 3 and rng.random() < .04:
                    c = mix(rng.choice(sprinkles), c, .4)
                self.fg[y][x] = c
            if t >= hz:
                # tufts where the ground meets the lake
                for k in range(1, int(noise.n1(x * .9 + 77) * 2.4 * self.unit) + 1):
                    if 0 <= t - k < h:
                        self.fg[t - k][x] = mix(body, top, .6)

        self._plant_big_trees(tops)

    def _plant_big_trees(self, tops):
        w, h = self.w, self.h
        rng, pal = self.rng, self.pal
        snow = mix(self._snow_colour(), pal["fg"], .3) if self.winter else None

        planned = []
        for side in (0, 1):
            for _ in range(max(2, int(w / 14))):
                dx = int(w * rng.random() ** 1.6 * .32)
                x = dx if side == 0 else w - 1 - dx
                edge = min(x, w - 1 - x)
                tall = h * rng.uniform(.10, .38) * (1 - .45 * edge / (w * .32))
                planned.append((tall, x, rng.uniform(.26, .36)))
        planned.sort()      # small ones first so the big ones end up in front

        for tall, x, fat in planned:
            tall = max(3, int(tall))
            col = mix(pal["fg"], pal["land"], clamp(1 - tall / (h * .42)) * .4)
            trees.pine(self.fg, x, tops[x] + 1, tall, col, col, 1,
                       fat=fat, snow=snow, trunk=3)

    # ------------------------------------------------------------------
    # things that move: birds, fireflies, falling snow/leaves

    def _scatter_life(self):
        rng = self.rng
        self.cloud_cover = self.sea["cloud"] + rng.uniform(-.04, .04)
        self.cloud_offset = (rng.uniform(0, 500), rng.uniform(0, 500))
        self._place_birds()
        self._place_fireflies()
        self._place_falling()

    def _place_birds(self):
        w, h, hz = self.w, self.h, self.horizon
        rng = self.rng
        self.birds = []
        self.bird_span = max(3.4, h * .035)       # half the wingspan, in pixels
        if self.night or h < 36:
            return
        speed = rng.uniform(1.5, 3) * w / 110      # the whole flock flies together
        count = rng.choice(self.sea["birds"]) * max(1, w // 110)
        for _ in range(count):
            for _try in range(30):
                bx, by = rng.uniform(0, w), rng.uniform(hz * .12, hz * .55)
                # keep them apart so they don't pile up into one blob
                if all(min(abs(bx - ox), w - abs(bx - ox)) > self.bird_span * 4
                       or abs(by - oy) > self.bird_span * 3
                       for ox, oy, _, _ in self.birds):
                    self.birds.append((bx, by, speed, rng.random() * 6))
                    break

    def _place_fireflies(self):
        rng = self.rng
        self.flies = []
        # fireflies are a warm-weather thing
        warm = self.season in ("spring", "summer")
        if warm and (self.night or (self.season == "summer" and self.tod == "dusk")):
            for _ in range(max(6, self.w // 9)):
                self.flies.append((rng.uniform(0, self.w),
                                   rng.uniform(self.h * .62, self.h - 3),
                                   rng.random() * 6.28))

    def _place_falling(self):
        rng = self.rng
        self.falling = []
        kind = self.sea["falling"]
        if kind is None:
            return
        self.fall = FALLING[kind]
        if kind == "snow":
            colours = [self._snow_colour()]
        elif kind == "leaves":
            colours = [self._lit(c) for c in self.sea["leaves"]]
        else:
            colours = [self._lit((255, 190, 215))]
        lo, hi = self.fall["speed"]
        big = self.h >= 120
        for _ in range(max(3, int(self.w * self.h / self.fall["per"]))):
            depth = rng.random()                      # 0 = far away, 1 = close
            colour = mix(rng.choice(colours), self.haze, (1 - depth) * .35)
            self.falling.append((
                rng.uniform(0, self.w), rng.uniform(0, self.h),
                rng.uniform(lo, hi) * self.unit * (.6 + .4 * depth),
                rng.random() * 6.28, colour, .3 + .35 * depth,
                2 if big and depth > .8 else 1))

    # ------------------------------------------------------------------
    # drawing a frame

    def frame(self, t=0.0):
        buf = [[None] * self.w for _ in range(self.h)]
        self._draw_sky_and_land(buf, t)
        self._draw_stars(buf, t)
        self._overlay_foreground(buf, 0, self.horizon)   # so the trees reflect
        self._draw_lake(buf, t)
        self._overlay_foreground(buf, self.horizon, self.h)
        self._draw_birds(buf, t)
        self._draw_fireflies(buf, t)
        self._draw_falling(buf, t)
        return buf

    def _draw_sky_and_land(self, buf, t):
        w, hz, noise = self.w, self.horizon, self.noise
        ox, oy = self.cloud_offset
        cx, cy = .022 * self.nx, .075 * self.ny
        cover = self.cloud_cover
        for y in range(hz):
            land_row, sky_row, row = self.land[y], self.sky[y], buf[y]
            # fewer clouds right at the top and right at the horizon
            fade = smoothstep(0, .12, y / hz) * (1 - smoothstep(.75, 1.0, y / hz) * .6)
            for x in range(w):
                c = land_row[x]
                if c is None:
                    c = sky_row[x]
                    px, py = x * cx + t * .05 + ox, y * cy + oy
                    density = noise.fbm2(px, py, 4)
                    alpha = smoothstep(cover, cover + .18, density) * fade
                    if alpha > .01:
                        c = self._cloud(c, x, y, px, py, density, alpha, cx, cy)
                row[x] = c

    def _cloud(self, c, x, y, px, py, density, alpha, cx, cy):
        # look a little way towards the sun: thinner there means that edge is lit
        d = math.hypot(self.sun_x - x, self.sun_y - y) or 1
        toward = self.noise.fbm2(px + (self.sun_x - x) / d * 2.5 * cx,
                                 py + (self.sun_y - y) / d * 2.5 * cy, 4)
        lit = clamp(.55 + (density - toward) * 6)
        return mix(c, mix(self.cloud_shade, self.cloud_light, lit), alpha * .92)

    def _draw_stars(self, buf, t):
        for x, y, bright, phase in self.stars:
            if self.land[y][x] is None:
                twinkle = .65 + .35 * math.sin(t * 2 + phase * 6.28)
                buf[y][x] = mix(buf[y][x], (255, 250, 235), bright * twinkle)

    def _overlay_foreground(self, buf, y0, y1):
        for y in range(y0, y1):
            row, fg = buf[y], self.fg[y]
            for x in range(self.w):
                if fg[x] is not None:
                    row[x] = fg[x]

    def _ice(self, x, dy, k):
        """How frozen the lake is here, 0..1. The edges freeze first."""
        edge = 1 - min(x, self.w - 1 - x) / (self.w * .5)
        n = self.noise.n2(x * .07 * self.nx, dy * .18 * self.ny + 11)
        return smoothstep(.40, .62, n + edge * .25 + k * .15)

    def _draw_lake(self, buf, t):
        w, h, hz = self.w, self.h, self.horizon
        pal, noise = self.pal, self.noise
        deep = max(1, h - hz - 1)
        ice_col = mix(self._lit((205, 225, 242)), self.haze, .3)

        for y in range(hz, h):
            dy = y - hz
            k = dy / deep
            mirrored = buf[max(0, hz - 1 - int(dy * .85))]
            spread = self.sun_r * 1.2 + dy * .35
            row = buf[y]
            for x in range(w):
                ice = self._ice(x, dy, k) if self.winter else 0
                # ripples shove the reflection sideways, frozen water doesn't ripple
                wobble = math.sin(dy * 1.2 + x * .045 * self.nx + t * 1.4) * (.6 + dy * .12)
                src = mirrored[min(w - 1, max(0, x + int(round(wobble * (1 - ice)))))]
                c = mix(src, pal["water"], .30 + .35 * k)
                c = scale(c, 1 + .05 * math.sin(dy * 2.3 + x * .3 + t * 2))
                if ice:
                    c = mix(c, ice_col, ice * .8)
                    crack = abs(noise.n2(x * .2 * self.nx, dy * .6 * self.ny + 3) - .5)
                    if ice > .6 and crack < .025:
                        c = scale(c, .85)
                # the sparkly path under the sun
                ds = abs(x - self.sun_x)
                if ds < spread:
                    g = noise.n2(x * .35 * self.nx, dy * 1.6 * self.ny + t * 1.2)
                    sparkle = smoothstep(.62, .85, g) * (1 - ds / spread) ** 1.3
                    c = mix(c, pal["sun"], sparkle * (.6 if self.night else .85) * (1 - ice))
                row[x] = c

    def _draw_birds(self, buf, t):
        if not self.birds:
            return
        w, h = self.w, self.h
        ink = mix(self.pal["land"], (0, 0, 0), .45)
        span = self.bird_span
        lift = max(2.0, span * .6)
        steps = int(span * 3) + 3
        for bx, by, speed, phase in self.birds:
            cx = (bx + t * speed) % w
            cy = by + math.sin(t * .8 + phase) * span * .4
            up = (math.sin(t * 6 + phase) + 1) / 2        # 0 = wings down, 1 = wings up
            # each wing is body -> elbow -> tip. Wings up makes a V, down makes
            # a roof with drooping tips, in between it's the flat gull shape.
            elbow = (span * .5, -lift * (.5 + .4 * up))
            tip = (span, lift * (.6 - 1.7 * up))
            points = [(0, 0), elbow, tip]
            for side in (-1, 1):
                for (x0, y0), (x1, y1) in zip(points, points[1:]):
                    for i in range(steps + 1):
                        u = i / steps
                        px = int(round(cx + side * (x0 + (x1 - x0) * u)))
                        py = int(round(cy + y0 + (y1 - y0) * u))
                        if 0 <= px < w and 0 <= py < h:
                            buf[py][px] = mix(buf[py][px], ink, .9)

    def _draw_fireflies(self, buf, t):
        for x0, y0, phase in self.flies:
            blink = max(0, math.sin(t * 2.2 + phase * 5)) ** 2
            if blink < .05:
                continue
            x = int(x0 + math.sin(t * .7 + phase) * 3)
            y = int(y0 + math.cos(t * .5 + phase * 2) * 2)
            for dx, dy, a in ((0, 0, 1), (1, 0, .3), (-1, 0, .3), (0, 1, .3), (0, -1, .3)):
                px, py = x + dx, y + dy
                if 0 <= px < self.w and 0 <= py < self.h:
                    buf[py][px] = mix(buf[py][px], (200, 255, 120), a * blink)

    def _draw_falling(self, buf, t):
        if not self.falling:
            return
        w, h = self.w, self.h
        wind, sway = self.fall["wind"], self.fall["sway"]
        for x0, y0, speed, phase, colour, alpha, size in self.falling:
            y = (y0 + t * speed) % h
            x = (x0 + t * wind + math.sin(t * .8 + phase) * sway) % w
            px, py = int(x), int(y)
            for dx in range(size):
                for dy in range(size):
                    if 0 <= px + dx < w and 0 <= py + dy < h:
                        buf[py + dy][px + dx] = mix(buf[py + dy][px + dx], colour, alpha)
