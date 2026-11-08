"""Command line handling and the live loop."""

import argparse
import random
import sys
import time

from . import __version__, terminal
from .palette import SEASONS, TIMES
from .scene import Scene, crossfade

HELP = """\
usage: evercland [OPTION]...

evercland is a terminal landscape generator: mountains, a lake, a forest and
whatever the sky and the season feel like today.

options:
  -l, --live            live mode: clouds drift, water moves, snow falls
  -i, --infinite        infinite mode: keep making new landscapes (implies -l)
  -w, --wait=SEC        seconds between landscapes in infinite mode [default: 20]
  -t, --time=SEC        seconds between frames in live mode [default: 0.1]
  -S, --screensaver     screensaver mode: -l -i, and any key quits
  -d, --daytime=TIME    dawn, day, dusk, night, auto or random [default: random]
  -e, --season=SEASON   spring, summer, autumn, winter, auto or random [default: random]
  -s, --seed=N          seed for the random number generator
  -a, --aspect=RATIO    pixel height/width, if the sun looks squashed or stretched
  -m, --message=TEXT    show a message under the landscape
  -p, --print           print the last frame when you quit live mode
  -v, --verbose         show the seed, season and time of day
  -V, --version         print the version and exit
  -h, --help            show this help

in live mode press q to quit.

examples:
  evercland                        one random landscape
  evercland -d dusk -e autumn      an autumn evening
  evercland -l -d auto -e auto     live view that follows your clock and calendar
  evercland -S                     screensaver
"""

FADE_FRAMES = 10


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("evercland: %s\nTry 'evercland --help' for more information.\n" % message)
        sys.exit(2)


def parse_args(argv):
    p = Parser(prog="evercland", add_help=False, allow_abbrev=False)
    p.add_argument("-l", "--live", action="store_true")
    p.add_argument("-i", "--infinite", action="store_true")
    p.add_argument("-w", "--wait", type=float, default=20)
    p.add_argument("-t", "--time", type=float, default=.1)
    p.add_argument("-S", "--screensaver", action="store_true")
    p.add_argument("-d", "--daytime", default="random", choices=(*TIMES, "auto", "random"))
    p.add_argument("-e", "--season", default="random", choices=(*SEASONS, "auto", "random"))
    p.add_argument("-s", "--seed", type=int)
    p.add_argument("-a", "--aspect", type=float)
    p.add_argument("-m", "--message")
    p.add_argument("-p", "--print", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("-V", "--version", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    return p.parse_args(argv)


# -- picking what to draw ----------------------------------------------

def auto_daytime():
    hour = time.localtime().tm_hour
    if 5 <= hour < 8:
        return "dawn"
    if 8 <= hour < 17:
        return "day"
    if 17 <= hour < 20:
        return "dusk"
    return "night"


def auto_season():
    # northern hemisphere, sorry
    month = time.localtime().tm_mon
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    if month in (9, 10, 11):
        return "autumn"
    return "winter"


def resolve(choice, names, auto, rng):
    if choice == "random":
        return rng.choice(names)
    if choice == "auto":
        return auto()
    return choice


def new_seed():
    return random.randrange(10 ** 6)


class Show:
    """One landscape, built to fit a particular terminal size."""

    def __init__(self, opts, seed, size, live):
        self.seed = seed
        self.size = size
        # time of day and season come from the seed unless they were asked for
        self.tod = resolve(opts.daytime, TIMES, auto_daytime, random.Random(seed))
        self.season = resolve(opts.season, SEASONS, auto_season, random.Random(seed + 1))

        cols, rows = size
        spare = 0 if live else 1              # leave room for the shell prompt
        if opts.message or opts.verbose:
            spare += 1                        # and for the caption
        self.w = max(20, cols)
        self.h = max(8, rows - spare) * 2
        aspect = opts.aspect or terminal.cell_aspect()
        self.scene = Scene(self.w, self.h, seed, self.tod, self.season, aspect)

    def caption(self, opts):
        bits = []
        if opts.message:
            bits.append(opts.message)
        if opts.verbose:
            bits.append("seed %d, %s, %s" % (self.seed, self.season, self.tod))
        return "  ".join(bits)


def render(show, buf, opts, live):
    text = terminal.to_ansi(buf)
    caption = show.caption(opts)
    if not caption:
        return text
    if live:
        rows = show.size[1]
        return text + "\x1b[%d;1H\x1b[2m  %s\x1b[0m\x1b[K" % (rows, caption)
    return text + "\n\x1b[2m  %s\x1b[0m" % caption


# -- the two modes -----------------------------------------------------

def still(opts):
    seed = opts.seed if opts.seed is not None else new_seed()
    show = Show(opts, seed, terminal.size(), live=False)
    sys.stdout.write(render(show, show.scene.frame(0.0), opts, False) + "\n")


def wants_out(key, opts):
    if key is None:
        return False
    if opts.screensaver:
        return True
    # a lone escape quits, arrow keys arrive as "\x1b[A" and don't count
    return key in ("q", "Q", "\x1b")


def fade_to(screen, opts, old, new, started):
    step = min(opts.time, .08)
    for i in range(1, FADE_FRAMES + 1):
        t = time.monotonic() - started
        buf = crossfade(old.scene.frame(t), new.scene.frame(t), i / FADE_FRAMES)
        screen.draw(render(new, buf, opts, True))
        time.sleep(step)


def live(opts):
    seed = opts.seed if opts.seed is not None else new_seed()
    started = time.monotonic()
    last = None

    with terminal.Screen() as screen:
        show = Show(opts, seed, terminal.size(), True)
        next_swap = started + opts.wait
        try:
            while True:
                frame_start = time.monotonic()
                if wants_out(screen.key(), opts):
                    break

                size = terminal.size()
                if size != show.size:
                    # window got resized, rebuild the same landscape to fit
                    show = Show(opts, show.seed, size, True)
                    screen.clear()

                if opts.infinite and frame_start >= next_swap:
                    fresh = Show(opts, new_seed(), show.size, True)
                    fade_to(screen, opts, show, fresh, started)
                    show = fresh
                    next_swap = time.monotonic() + opts.wait
                    continue

                buf = show.scene.frame(frame_start - started)
                screen.draw(render(show, buf, opts, True))
                last = (show, buf)
                time.sleep(max(0, opts.time - (time.monotonic() - frame_start)))
        except KeyboardInterrupt:
            pass

    if opts.print and last:
        show, buf = last
        sys.stdout.write(render(show, buf, opts, False) + "\n")


def main(argv=None):
    opts = parse_args(argv)
    if opts.help:
        sys.stdout.write(HELP)
        return 0
    if opts.version:
        print("evercland", __version__)
        return 0

    opts.wait = max(1.0, opts.wait)
    opts.time = max(.02, opts.time)
    if opts.screensaver:
        opts.live = opts.infinite = True
    if opts.infinite:
        opts.live = True

    if opts.live and sys.stdout.isatty():
        live(opts)
    else:
        still(opts)       # piped output (or no tty): just print one picture
    return 0
