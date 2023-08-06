#!/usr/bin/env python3
#
# Stream-based realtime scientific data plotter.
# Copyright (c) 2022, Hiroyuki Ohsaki.
# All rights reserved.
#

import contextlib
import math

# Disable the banner when loading pygame modules.
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.gfxdraw
import curses
from functools import cache

from perlcompat import die, warn, getopts
import tbdump

FONT_SIZE = 14

BLACK = (0, 0, 0)

# Internal color numbers.
DARK_GRAY = 100
GRAY = 101
WHITE = 102

# This code is taken from cellx/monitor/color.py.
@cache
def hsv2rgb(h, s, v):
    """Convert color in HSV (Hue, Saturation, Value) space to RGB.  Return (R,
    G, B) as a list.  Transformation algorithm is taken from
    http://psychology.wikia.com/wiki/HSV_color_space."""
    hi = int(h / 60) % 6
    f = h / 60 - hi
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if hi == 0:
        return v, t, p
    elif hi == 1:
        return q, v, p
    elif hi == 2:
        return p, v, t
    elif hi == 3:
        return p, q, v
    elif hi == 4:
        return t, p, v
    elif hi == 5:
        return v, p, q

class Series(list):
    def __init__(self,
                 id_=None,
                 vmin=0,
                 vmax=.01,
                 color=None,
                 fill=False,
                 label=None,
                 hide=False):
        self.id_ = id_
        self.vmin = vmin
        self.vmax = vmax
        if color is None:
            color = id_
        self.color = color
        self.fill = fill
        if label is None:
            label = f'#{id_}'
        self.label = label
        self.hide = False
        self.vsum = 0  # Used for obtaining the sample mean.

    def __repr__(self):
        return f'Series(id_={self.id_}, vmin={self.vmin}, vmax={self.vmax}, color={self.color}, label={self.label}, hide={self.hide}, len={len(self)}'

    def append(self, v):
        # Update the minimum and the maximum value at the time of data storage.
        if v < self.vmin:
            self.vmin = v
        if v > self.vmax:
            self.vmax = v
        self.vsum += v
        super().append(v)

    def at(self, ratio, left, right):
        """Return a value located at the ratio of RATIO in samples between
        LEFT and RIGHT.  If LEFT or RIGHT is negative, the offset is regarded
        from the end."""
        if left < 0:
            left = max(len(self) + left, 0)
        if right < 0:
            right += len(self)
        n = int(left + (right - left) * ratio)
        return self[n]

class Plot:
    def __init__(self,
                 screen=None,
                 width=None,
                 height=None,
                 offset=None,
                 left=0,
                 right=-1,
                 grid=None,
                 xgrid=None,
                 start_color=0):
        self.screen = screen
        if screen:
            if width is None:
                width = self.screen.width
            if height is None:
                height = self.screen.height
        self.width = width
        self.height = height
        if offset is None:
            offset = 0, 0
        self.offset = offset
        self.left = left
        self.right = right
        self.grid = grid
        self.xgrid = xgrid
        self.start_color = start_color
        self._series = []
        self.vmin = None
        self.vmax = None

    def __repr__(self):
        return f'Plot(width={self.width}, height={self.height}, offset={self.offset}, left={self.left}, right={self.right}, grid={self.grid}, xgrid={self.xgrid}, vmin={self.vmin}, vmax={self.vmax}, _series={self._series})'

    # Series handling.
    def series(self, n):
        """Return the object for N-th seriries.  The object is newly created
        if it does not exist."""
        while len(self._series) - 1 < n:
            sr = Series(1 + n, color=self.start_color + n)
            self._series.append(sr)
        return self._series[n]

    def visible_series(self):
        """Return all Seriries object, which are available as well as being
        not hidden."""
        return [sr for sr in self._series if len(sr) > 0 and not sr.hide]

    def update_minmax(self, series=None):
        """Find the maximum and the minimum values of all series."""
        if series is None:
            series = [sr for sr in self._series if not sr.hide]
        self.vmin = min([sr.vmin for sr in series])
        self.vmax = max([sr.vmax for sr in series])

    def to_y_coordinate(self, v):
        """Assuming that the y-axis ranges from the minimum and the maximum
        value, return the y-axsis of the value V.  For instance, if V is eqaul
        to the minimum, this function returns the value of SELF.HEIGHT."""
        margin = int(self.height * .01)
        height = int(self.height * .98)
        return margin + int(height - height * (v - self.vmin) /
                            (self.vmax - self.vmin))

    def draw_single_series(self, sr):
        """Draw a line for the seriries object SR as a concatenation of short
        line segments."""
        margin = int(self.width * .01)
        width = int(self.width * .98)
        x0, y0 = None, None
        for x in range(width):
            ratio = x / width
            v = sr.at(ratio, self.left, self.right)
            y = self.to_y_coordinate(v)
            if x > 0:
                self.screen.draw_line(margin + x0,
                                      y0,
                                      margin + x,
                                      y,
                                      sr.color,
                                      offset=self.offset)
                if sr.fill:
                    self.screen.draw_line(margin + x,
                                          y,
                                          margin + x,
                                          self.height,
                                          sr.color,
                                          alpha=32,
                                          offset=self.offset)
            x0, y0 = x, y

    def auto_grid(self, vmin=None, vmax=None):
        if vmin is None:
            vmin = self.vmin
        if vmax is None:
            vmax = self.vmax
        if vmin is None or vmax is None:
            return None
        delta = vmax - vmin
        if delta <= 0:
            return None
        digits = int(math.log(delta) / math.log(10))
        return 10**digits

    def find_grids(self, grid=None, vmin=None, vmax=None):
        if grid is None:
            grid = self.grid
        if vmin is None:
            vmin = self.vmin
        if vmax is None:
            vmax = self.vmax
        if vmax - vmin < grid:
            return
        # How many grid lines should be drawn?
        ngrids = vmin / grid
        n = int(ngrids)
        remainder = vmin - grid * n
        # FIXME: Fail if vmin is negative?
        v = self.vmin - grid * remainder
        while v < vmax:
            if vmin <= v:
                yield v
            v += grid

    def draw_grid(self, grid, color):
        """Draw grids for y-axis.  The interval between grids is spcified by
        GRID.  Its color is specified by COLOR."""
        # How many grid lines should be drawn?
        for v in self.find_grids(grid):
            y = self.to_y_coordinate(v)
            # FIXME: It's better to control the brightntess with alpha channel.
            self.screen.draw_line(0,
                                  y,
                                  self.width,
                                  y,
                                  color,
                                  offset=self.offset)

    def draw_xgrid(self, xgrid, color):
        sr = self.series(0)
        xl, xr = sr[self.left], sr[self.right]
        for v in self.find_grids(xgrid, xl, xr):
            x = int(self.width * (v - xl) / (xr - xl))
            self.screen.draw_line(x,
                                  0,
                                  x,
                                  self.height,
                                  color,
                                  offset=self.offset)

    def draw_legends(self):
        """Draw legends for all lines plotted."""
        # NOTE: legends are shown also for hidden serries.
        for n, sr in enumerate(self._series):
            x = 1
            y = 1 + n * FONT_SIZE
            v = sr[self.right]
            # Display field label.
            self.screen.draw_text(x, y, sr.label, sr.color, offset=self.offset)
            # Display current, mean, and maximum values.
            mean = sr.vsum / len(sr)
            self.screen.draw_text(x + FONT_SIZE * 3,
                                  y,
                                  f'{v:9.2f} AVG{mean:9.2f} MAX{sr.vmax:9.2f}',
                                  sr.color,
                                  offset=self.offset)

    def draw_series(self):
        """Draw all series excluding hidden ones.  The range of the y-axis is
        automatically determined."""
        series = self.visible_series()
        if not series:
            return
        self.update_minmax(series)
        # Draw grid line.
        if self.grid:
            if not self.screen.curses:
                self.draw_grid(self.grid / 2, DARK_GRAY)
            self.draw_grid(self.grid, GRAY)
        if self.xgrid:
            if not self.screen.curses:
                self.draw_xgrid(self.xgrid / 2, DARK_GRAY)
            self.draw_xgrid(self.xgrid, GRAY)
        # Draw all series.
        for sr in series:
            self.draw_single_series(sr)
        # Draw legends.
        self.draw_legends()
        # Display the maximum and the minimum values.
        self.screen.draw_text(-FONT_SIZE * 5,
                              0,
                              f'{self.vmax:8.2f}',
                              self.start_color,
                              offset=self.offset,
                              plot=self)
        self.screen.draw_text(-FONT_SIZE * 5,
                              -FONT_SIZE * 2,
                              f'{self.vmin:8.2f}',
                              self.start_color,
                              offset=self.offset,
                              plot=self)

    @cache
    def create_background(self):
        surface = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            alpha = int(48 * y / self.height)
            self.screen.draw_line(0,
                                  y,
                                  self.width,
                                  y,
                                  self.start_color,
                                  alpha=alpha,
                                  surface=surface)
        return surface

    def draw_background(self):
        """Fill the background with gradient colors."""
        # FIXME: Should not re-generate at every drawing.
        if not self.screen.curses:
            bg = self.create_background()
            self.screen.screen.blit(bg, self.offset)

class Screen:
    def __init__(self,
                 curses=False,
                 width=None,
                 height=None,
                 fullscreen=False):
        self.curses = curses
        # Uses SVGA (800x600 pixels) window by default.
        if not curses and (width is None or height is None):
            if fullscreen:
                width, height = 1920, 1080
            else:
                width, height = 800, 600
        self.width = width
        self.height = height
        self._rplots = []
        self.init_screen()

    def __repr__(self):
        return f'Screen(curses={self.curses}, width={self.width}, height={self.height})'

    @cache
    def color_rgba(self, n, alpha=255):
        """Return 8-bit RGBA color for the color number N as a tuple.  The
        alpha channel is given by ALPHA."""
        if n == DARK_GRAY:
            return 32, 32, 32
        if n == GRAY:
            return 64, 64, 64
        if n == WHITE:
            return 255, 255, 255
        # Pick distinctive colors from HSV color space in this order.
        plist = [n / 10 for n in [6, 8, 1, 10, 0, 4, 9, 2, 5, 3, 7]]
        i = n % len(plist)
        r, g, b = hsv2rgb(255 * plist[i], .6, 1.)
        return int(r * 255), int(g * 255), int(b * 255), alpha

    # Draw primitives.
    def init_screen(self):
        """Initialize the screen according to the output device."""
        if not self.curses:
            pygame.display.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.font.init()
        else:
            self.screen = curses.initscr()
            curses.start_color()
            self.height, self.width = self.screen.getmaxyx()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
            self.screen.erase()

    def draw_line(self,
                  x1,
                  y1,
                  x2,
                  y2,
                  color=0,
                  offset=None,
                  alpha=255,
                  surface=None):
        """Draw a straight line connecting two points: (X1, Y1) and (X2, Y2).
        The line color can b especified by COLOR and ALPHA."""
        if offset is None:
            offset = 0, 0
        dx, dy = offset
        x1, y1 = x1 + dx, y1 + dy
        x2, y2 = x2 + dx, y2 + dy
        if not self.curses:
            if surface is None:
                surface = self.screen
            rgba = self.color_rgba(color, alpha)
            pygame.gfxdraw.line(surface, x1, y1, x2, y2, rgba)
            return

        # Curses only.
        # Change the point style for different line colors.
        points = ['●', '■', '◆', '▲', '▼', '◼', '○', '□', '◇', '△', '▽', '◻']
        point = points[color % len(points)]

        # NOTE: These colors are only for drawing major and minor grids.
        if color == GRAY:
            point = '.'
            color = 1
        if color == DARK_GRAY:
            point = '-'
            color = 1

        # A classical (and inefficient) line draing algorithm.
        if abs(x1 - x2) >= abs(y1 - y2):
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            for x in range(x1, x2):
                y = int(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
                self.draw_text(x, y, point, color)
        else:
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            for y in range(y1, y2):
                x = int(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
                self.draw_text(x, y, point, color)

    @cache
    def load_font(self, name, size, bold=False):
        return pygame.font.SysFont(name, size, bold=bold)

    def draw_text(self,
                  x,
                  y,
                  text,
                  color=0,
                  size=FONT_SIZE,
                  offset=None,
                  plot=None,
                  _cache=[]):
        """Display a text TEXT at the location of (X, Y).  Font size and color
        can be specified with COLOR and SIZE."""
        if offset is None:
            offset = 0, 0
        dx, dy = offset
        if not self.curses:
            # Negative coordinate indicates the distance from the oppsosite edge.
            if x < 0:
                x = self.width + x
            if y < 0:
                y = self.height + y
            font = self.load_font('Courier', size, bold=True)
            rgba = self.color_rgba(color)
            # The second parameter True means enabling antialiasing.
            text = font.render(text, True, rgba, BLACK)
            self.screen.blit(text, (dx + x, dy + y))
        else:
            if len(text) >= 2:
                # Negative coordinate indicates the distance from the oppsosite edge.
                if x < 0:
                    x = plot.width * FONT_SIZE // 2 + x
                if y < 0:
                    y = plot.height * FONT_SIZE + y
                x = int(x // (FONT_SIZE / 2))
                y = int(y // FONT_SIZE)
            attr = curses.color_pair(1 + color % 7)
            try:
                self.screen.addstr(dy + y, dx + x, text, attr)
            except:
                pass

    def clear(self):
        """Clear the eintire screen."""
        if not self.curses:
            self.screen.fill(BLACK)
        else:
            self.screen.erase()

    def update(self):
        """Update the screen to relfenct recent changes."""
        if not self.curses:
            pygame.display.update()
        else:
            self.screen.refresh()

    def wait(self):
        """Wait until any key will be pressed."""
        if not self.curses:
            while True:
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    return
        else:
            # Not necessary in curses mode.
            pass

    def scan_key(self):
        if not self.curses:
            # Pump event as much as possible.
            while True:
                event = pygame.event.poll()
                if event.type == pygame.NOEVENT:
                    return None
                if event.type == pygame.KEYDOWN:
                    return event.unicode
        else:
            # Not necessary in curses mode.
            self.screen.nodelay(True)
            try:
                key = self.screen.getkey()
                return key
            except:
                return None
