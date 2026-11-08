# evercland

A terminal landscape generator. Mountains, a lake, a forest, and a sky that
changes with the time of day and the season. Pure python, no dependencies, but
you need a truecolor terminal (kitty, alacritty, foot, wezterm, ...).

```
evercland                       one random landscape
evercland -d dusk -e autumn     an autumn evening
evercland -l -d auto -e auto    live view that follows your clock and calendar
evercland -S                    screensaver
```

## options

```
  -l, --live            live mode: clouds drift, water moves, snow falls
  -i, --infinite        infinite mode: keep making new landscapes (implies -l)
  -w, --wait=SEC        seconds between landscapes in infinite mode [20]
  -t, --time=SEC        seconds between frames in live mode [0.1]
  -S, --screensaver     screensaver mode: -l -i, and any key quits
  -d, --daytime=TIME    dawn, day, dusk, night, auto or random [random]
  -e, --season=SEASON   spring, summer, autumn, winter, auto or random [random]
  -s, --seed=N          seed for the random number generator
  -a, --aspect=RATIO    pixel height/width, if the sun looks squashed or stretched
  -m, --message=TEXT    show a message under the landscape
  -p, --print           print the last frame when you quit live mode
  -v, --verbose         show the seed, season and time of day
  -V, --version         print the version and exit
  -h, --help            show this help
```

Same seed + same size + same `-d`/`-e` gives the same picture, so if you find
one you like, `-v` tells you the seed.

In live mode the picture follows the window if you resize it. Press `q` to quit.

## seasons

- **spring** pink blossoms, flowers on the shore, drifting petals
- **summer** deep green, hardly any snow, fireflies in the evening
- **autumn** orange and red trees, leaves falling, big flocks of birds
- **winter** snowy mountains, bare trees, snow on the pines, a half frozen lake, snowfall

`auto` for the season goes by the calendar (northern hemisphere).

## install

Run it straight from the checkout:

```
./evercland
```

or install it:

```
sudo make install            # to /usr/local, set PREFIX= to change that
makepkg -si                  # or as a pacman package, from this directory
```

## layout

```
evercland              launcher
src/evercland/
  cli.py            arguments, live loop, infinite mode
  scene.py          builds the landscape and draws frames
  trees.py          pine, broadleaf and bare tree sprites
  palette.py        colours, and what each season changes
  terminal.py       ansi output, window size, raw keys
  colors.py         colour maths
  noise.py          value noise
```

## notes

- It draws with half blocks, so every character is two pixels tall. A cell is
  usually a little taller than 2:1, evercland reads the real size from the
  terminal to keep the sun round. If your terminal doesn't report its pixel
  size (some multiplexers don't) use `-a 1.2` or thereabouts.
- Big windows take a moment to build, a 300x170 pixel canvas is about half a second.
