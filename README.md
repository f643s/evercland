# evercland

**a place in the dreams, in the terminal.**

A small pond, a ring of trees, mountains behind it, and a sky that moves with
the hour and the season. Evercland draws all of that in half blocks, in
truecolor, in whatever window you give it — and nothing else.

No dependencies. Pure Python. One file in, one picture out.

![an autumn evening in evercland](assets/hero.webp)

<sub>178 × 53 cells, seed 7, autumn, dusk.</sub>

---

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

It wants Python 3 and a truecolor terminal — kitty, alacritty, foot, wezterm,
anything modern. On a terminal that can't do 24-bit colour, it will look like a
sad grey smear.

## use

```
evercland                       one random landscape
evercland -d dusk -e autumn     an autumn evening
evercland -l -d auto -e auto    live view that follows your clock and calendar
evercland -S                    screensaver
```

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

In live mode the picture follows the window if you resize it. Press `q` to quit.

Same seed, same size, same `-d` and `-e` gives the same picture — so when you
find one you like, `-v` tells you the seed to get it back.

## the seasons

Every frame below is **seed 7**. Only the hour and the season change, so you can
watch the palette do all the work.

<table>
  <tr>
    <th></th>
    <th>dawn</th>
    <th>day</th>
    <th>dusk</th>
    <th>night</th>
  </tr>
  <tr>
    <th align="right">spring</th>
    <td><img src="assets/178x53/spring-dawn.webp" width="178" alt="spring at dawn"></td>
    <td><img src="assets/178x53/spring-day.webp" width="178" alt="spring in the day"></td>
    <td><img src="assets/178x53/spring-dusk.webp" width="178" alt="spring at dusk"></td>
    <td><img src="assets/178x53/spring-night.webp" width="178" alt="spring at night"></td>
  </tr>
  <tr>
    <th align="right">summer</th>
    <td><img src="assets/178x53/summer-dawn.webp" width="178" alt="summer at dawn"></td>
    <td><img src="assets/178x53/summer-day.webp" width="178" alt="summer in the day"></td>
    <td><img src="assets/178x53/summer-dusk.webp" width="178" alt="summer at dusk"></td>
    <td><img src="assets/178x53/summer-night.webp" width="178" alt="summer at night"></td>
  </tr>
  <tr>
    <th align="right">autumn</th>
    <td><img src="assets/178x53/autumn-dawn.webp" width="178" alt="autumn at dawn"></td>
    <td><img src="assets/178x53/autumn-day.webp" width="178" alt="autumn in the day"></td>
    <td><img src="assets/178x53/autumn-dusk.webp" width="178" alt="autumn at dusk"></td>
    <td><img src="assets/178x53/autumn-night.webp" width="178" alt="autumn at night"></td>
  </tr>
  <tr>
    <th align="right">winter</th>
    <td><img src="assets/178x53/winter-dawn.webp" width="178" alt="winter at dawn"></td>
    <td><img src="assets/178x53/winter-day.webp" width="178" alt="winter in the day"></td>
    <td><img src="assets/178x53/winter-dusk.webp" width="178" alt="winter at dusk"></td>
    <td><img src="assets/178x53/winter-night.webp" width="178" alt="winter at night"></td>
  </tr>
</table>

**spring** pink blossoms, flowers on the shore, drifting petals.
**summer** deep green, hardly any snow, fireflies in the evening.
**autumn** orange and red trees, leaves falling, big flocks of birds.
**winter** snowy mountains, bare trees, snow on the pines, a half frozen pond, snowfall.

`auto` for the season goes by the calendar (northern hemisphere, sorry).

## it fits any window

The same evening at three sizes. Everything is composed for the space it has —
no cropping, no scrolling, just fewer and bigger pixels as the window shrinks.

<table>
  <tr>
    <td align="center"><img src="assets/178x53/autumn-dusk.webp" width="356" alt="autumn dusk at 178 by 53"><br><sub>178 × 53</sub></td>
    <td align="center"><img src="assets/86x25/autumn-dusk.webp" width="344" alt="autumn dusk at 86 by 25"><br><sub>86 × 25</sub></td>
    <td align="center"><img src="assets/40x11/autumn-dusk.webp" width="320" alt="autumn dusk at 40 by 11"><br><sub>40 × 11</sub></td>
  </tr>
</table>

<details>
<summary>the two smaller sizes, all sixteen frames</summary>
<br>

**86 × 25**

<table>
  <tr>
    <th></th>
    <th>dawn</th>
    <th>day</th>
    <th>dusk</th>
    <th>night</th>
  </tr>
  <tr>
    <th align="right">spring</th>
    <td><img src="assets/86x25/spring-dawn.webp" width="172" alt="spring at dawn"></td>
    <td><img src="assets/86x25/spring-day.webp" width="172" alt="spring in the day"></td>
    <td><img src="assets/86x25/spring-dusk.webp" width="172" alt="spring at dusk"></td>
    <td><img src="assets/86x25/spring-night.webp" width="172" alt="spring at night"></td>
  </tr>
  <tr>
    <th align="right">summer</th>
    <td><img src="assets/86x25/summer-dawn.webp" width="172" alt="summer at dawn"></td>
    <td><img src="assets/86x25/summer-day.webp" width="172" alt="summer in the day"></td>
    <td><img src="assets/86x25/summer-dusk.webp" width="172" alt="summer at dusk"></td>
    <td><img src="assets/86x25/summer-night.webp" width="172" alt="summer at night"></td>
  </tr>
  <tr>
    <th align="right">autumn</th>
    <td><img src="assets/86x25/autumn-dawn.webp" width="172" alt="autumn at dawn"></td>
    <td><img src="assets/86x25/autumn-day.webp" width="172" alt="autumn in the day"></td>
    <td><img src="assets/86x25/autumn-dusk.webp" width="172" alt="autumn at dusk"></td>
    <td><img src="assets/86x25/autumn-night.webp" width="172" alt="autumn at night"></td>
  </tr>
  <tr>
    <th align="right">winter</th>
    <td><img src="assets/86x25/winter-dawn.webp" width="172" alt="winter at dawn"></td>
    <td><img src="assets/86x25/winter-day.webp" width="172" alt="winter in the day"></td>
    <td><img src="assets/86x25/winter-dusk.webp" width="172" alt="winter at dusk"></td>
    <td><img src="assets/86x25/winter-night.webp" width="172" alt="winter at night"></td>
  </tr>
</table>

**40 × 11**

<table>
  <tr>
    <th></th>
    <th>dawn</th>
    <th>day</th>
    <th>dusk</th>
    <th>night</th>
  </tr>
  <tr>
    <th align="right">spring</th>
    <td><img src="assets/40x11/spring-dawn.webp" width="160" alt="spring at dawn"></td>
    <td><img src="assets/40x11/spring-day.webp" width="160" alt="spring in the day"></td>
    <td><img src="assets/40x11/spring-dusk.webp" width="160" alt="spring at dusk"></td>
    <td><img src="assets/40x11/spring-night.webp" width="160" alt="spring at night"></td>
  </tr>
  <tr>
    <th align="right">summer</th>
    <td><img src="assets/40x11/summer-dawn.webp" width="160" alt="summer at dawn"></td>
    <td><img src="assets/40x11/summer-day.webp" width="160" alt="summer in the day"></td>
    <td><img src="assets/40x11/summer-dusk.webp" width="160" alt="summer at dusk"></td>
    <td><img src="assets/40x11/summer-night.webp" width="160" alt="summer at night"></td>
  </tr>
  <tr>
    <th align="right">autumn</th>
    <td><img src="assets/40x11/autumn-dawn.webp" width="160" alt="autumn at dawn"></td>
    <td><img src="assets/40x11/autumn-day.webp" width="160" alt="autumn in the day"></td>
    <td><img src="assets/40x11/autumn-dusk.webp" width="160" alt="autumn at dusk"></td>
    <td><img src="assets/40x11/autumn-night.webp" width="160" alt="autumn at night"></td>
  </tr>
  <tr>
    <th align="right">winter</th>
    <td><img src="assets/40x11/winter-dawn.webp" width="160" alt="winter at dawn"></td>
    <td><img src="assets/40x11/winter-day.webp" width="160" alt="winter in the day"></td>
    <td><img src="assets/40x11/winter-dusk.webp" width="160" alt="winter at dusk"></td>
    <td><img src="assets/40x11/winter-night.webp" width="160" alt="winter at night"></td>
  </tr>
</table>

</details>

## how it draws

Each character is an upper half block (`▀`). The foreground colour is the top
pixel, the background colour is the one under it, so every cell is two pixels
tall and the picture is built out of cells instead of an image buffer.

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

Everything is deterministic: value noise for the mountains, a seeded
`random.Random` for placement, a palette function for the light. No sprites are
stored, nothing is loaded from disk.

## notes

- A cell is usually a little taller than 2:1, so evercland reads the real pixel
  size from the terminal to keep the sun round. If your terminal doesn't report
  it (some multiplexers don't) use `-a 1.2` or thereabouts.
- Big windows take a moment to build. A 300 × 170 pixel canvas is about half a
  second.
- The gallery images are the program's own output, cell for cell, scaled up with
  nearest neighbour. No post-processing.

## license

GPL-3.0-or-later. See [COPYING](COPYING).
