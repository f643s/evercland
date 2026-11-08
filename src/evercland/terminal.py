"""Everything that touches the actual terminal: size, drawing, raw keys."""

import fcntl
import os
import select
import shutil
import struct
import sys
import termios
import tty

from .colors import clamp


def size():
    """(columns, rows)"""
    cols, rows = shutil.get_terminal_size((100, 32))
    return cols, rows


def cell_aspect():
    """Height / width of one half-block pixel.

    A cell is usually a bit taller than 2:1, so the "square" pixels aren't.
    We can work it out if the terminal tells us its size in pixels, otherwise
    just pretend they're square.
    """
    try:
        data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\0" * 8)
        rows, cols, xpix, ypix = struct.unpack("HHHH", data)
        if rows and cols and xpix and ypix:
            return clamp((ypix / rows / 2) / (xpix / cols), .7, 1.7)
    except (OSError, ValueError):
        pass
    return 1.0


def _byte(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def to_ansi(buf):
    """Turn a picture into a string of truecolor half blocks.

    Each character is an upper half block: the foreground colour is the top
    pixel and the background colour is the bottom one.
    """
    lines = []
    for y in range(0, len(buf) - 1, 2):
        top, bottom = buf[y], buf[y + 1]
        parts = []
        last = None
        for t, b in zip(top, bottom):
            colours = (_byte(t[0]), _byte(t[1]), _byte(t[2]),
                       _byte(b[0]), _byte(b[1]), _byte(b[2]))
            if colours != last:
                parts.append("\x1b[38;2;%d;%d;%d;48;2;%d;%d;%dm" % colours)
                last = colours
            parts.append("\u2580")
        parts.append("\x1b[0m")
        lines.append("".join(parts))
    return "\n".join(lines)


class Screen:
    """Alternate screen + hidden cursor + non-blocking keys, put back on exit."""

    def __init__(self):
        self.saved = None

    def __enter__(self):
        sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[2J")
        sys.stdout.flush()
        if sys.stdin.isatty():
            self.saved = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, *_):
        if self.saved is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.saved)
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()

    def clear(self):
        sys.stdout.write("\x1b[2J")

    def draw(self, text):
        sys.stdout.write("\x1b[H" + text)
        sys.stdout.flush()

    def key(self):
        """Whatever the user typed since last time, or None."""
        if self.saved is None:
            return None
        if select.select([sys.stdin], [], [], 0)[0]:
            return os.read(sys.stdin.fileno(), 32).decode(errors="ignore")
        return None
