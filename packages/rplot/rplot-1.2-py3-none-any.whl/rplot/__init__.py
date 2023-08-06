#!/usr/bin/env python3
#
#
# Copyright (c) 2022, Hiroyuki Ohsaki.
# All rights reserved.
#

import contextlib
import time

with contextlib.redirect_stdout(None):
    import pygame
    import pygame.gfxdraw
import curses

from perlcompat import die, warn, getopts
import tbdump

FONT_SIZE = 18

BLACK = (0, 0, 0)

DARK_GRAY = 100
GRAY = 101
WHITE = 102

# This code is taken from cellx/monitor/color.py.
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
    def __init__(self, id_=None, vmin=0, vmax=1, color=None, label=None):
        self.id_ = id_
        self.vmin = vmin
        self.vmax = vmax
        if color is None:
            color = id_
        self.color = color
        if label is None:
            label = f'#{id_}'
        self.label = label
        self.vsum = 0

    def __repr__(self):
        return f'Series(id_={self.id_}, vmin={self.vmin}, vmax={self.vmax}, color={self.color}, label={self.label}, len={len(self)}'

    def append(self, v):
        if v < self.vmin:
            self.vmin = v
        if v > self.vmax:
            self.vmax = v
        self.vsum += v
        super().append(v)

    def at(self, ratio, window=None):
        if window is None:
            n = int(len(self) * ratio)
            return self[n]
        if len(self) < window:
            return self.at(ratio, None)

        offset = len(self) - window
        n = int(offset + window * ratio)
        return self[n]

class Plot:
    def __init__(self,
                 screen=None,
                 width=None,
                 height=None,
                 offset=None,
                 grid=None,
                 subgrid=None,
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
        self.grid = grid
        self.subgrid = subgrid
        self.start_color = start_color
        self._series = []
        self.window = None
        self.vmin = None
        self.vmax = None
        self.excluded = []

    def __repr__(self):
        return f'Plot(grid={self.grid}, subgrid={self.subgrid}, _series={self._series})'

    # series handling
    def series(self, n):
        while len(self._series) - 1 < n:
            sr = Series(1 + n, color=self.start_color + n)
            self._series.append(sr)
        return self._series[n]

    def visible_series(self):
        for sr in self._series:
            if sr.id_ not in self.excluded:
                yield sr

    def v2y(self, v):
        return int(self.height - self.height * (v - self.vmin) /
                   (self.vmax - self.vmin))

    def draw_single_series(self, sr):
        if self.screen is None:
            die('draw_single_series: no screen found')
        x0, y0 = None, None
        for x in range(self.width):
            ratio = x / self.width
            v = sr.at(ratio, self.window)
            y = self.v2y(v)
            if x > 0:
                self.screen.draw_line(x0,
                                      y0,
                                      x,
                                      y,
                                      sr.color,
                                      offset=self.offset)
            x0, y0 = x, y

    def update_minmax(self, excluded=None):
        self.vmin = min([sr.vmin for sr in self.visible_series()])
        self.vmax = max([sr.vmax for sr in self.visible_series()])

    def draw_series(self, excluded=None):
        self.update_minmax(excluded)
        # Draw grid line.
        if self.subgrid:
            self.draw_grid(self.subgrid, DARK_GRAY)
        if self.grid:
            self.draw_grid(self.grid, GRAY)
        # Draw all series.
        for sr in self.visible_series():
            self.draw_single_series(sr)
        # Draw legends.
        # NOTE: legends are shown also for *excluded* serries
        self.draw_legends()
        # Draw ticks.
        self.screen.draw_text(self.width - FONT_SIZE * 6,
                              0,
                              f'{self.vmax:8.2f}',
                              WHITE,
                              offset=self.offset)
        self.screen.draw_text(self.width - FONT_SIZE * 6,
                              self.height - FONT_SIZE * 2,
                              f'{self.vmin:8.2f}',
                              WHITE,
                              offset=self.offset)

    def draw_grid(self, grid, color):
        ngrids = (self.vmax - self.vmin) / grid
        n = int(ngrids)
        if self.screen.curses and n > 5:
            return
        frac = ngrids - n
        v = self.vmin + grid * frac
        for i in range(n):
            y = self.v2y(v)
            self.screen.draw_line(0,
                                  y,
                                  self.width,
                                  y,
                                  color,
                                  offset=self.offset)
            v += grid

    def draw_legends(self):
        for n, sr in enumerate(self._series):
            x = 1
            y = 1 + n * FONT_SIZE
            v = sr[-1]
            self.screen.draw_text(x, y, sr.label, sr.color, offset=self.offset)
            mean = sr.vsum / len(sr)
            self.screen.draw_text(x + FONT_SIZE * 4,
                                  y,
                                  f'{v:8.2f}/{mean:8.2f}/{sr.vmax:8.2f}',
                                  sr.color,
                                  offset=self.offset)

class Screen:
    def __init__(self, curses=False, width=None, height=None):
        self.curses = curses
        if not curses and (width is None or height is None):
            width, height = 800, 600
        self.width = width
        self.height = height
        self._rplots = []
        self.init_screen()

    def __repr__(self):
        return f'Screen(curses={self.curses}, width={self.width}, height={self.height})'

    def color_rgb(self, n):
        if n == DARK_GRAY:
            return 32, 32, 32
        if n == GRAY:
            return 64, 64, 64
        if n == WHITE:
            return 255, 255, 255
        plist = [n / 10 for n in [6, 8, 1, 10, 0, 4, 9, 2, 5, 3, 7]]
        i = n % len(plist)
        r, g, b = hsv2rgb(255 * plist[i], .6, 1.)
        return int(r * 255), int(g * 255), int(b * 255)

    # draw primitives
    def init_screen(self):
        if not self.curses:
            pygame.display.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.font.init()
        else:
            self.screen = curses.initscr()
            curses.start_color()
            self.height, self.width = self.screen.getmaxyx()
            self.screen.erase()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

    def draw_line(self, x1, y1, x2, y2, color=0, offset=None):
        if offset is None:
            offset = 0, 0
        dx, dy = offset
        x1, y1 = x1 + dx, y1 + dy
        x2, y2 = x2 + dx, y2 + dy
        if not self.curses:
            rgb = self.color_rgb(color)
            pygame.gfxdraw.line(self.screen, x1, y1, x2, y2, rgb)
            return

        # Curses only.
        points = ['●', '■', '◆', '▲', '▼', '◼', '○', '□', '◇', '△', '▽', '◻']
        point = points[color % len(points)]

        if color == GRAY:
            point = '.'
            color = 1
        if color == DARK_GRAY:
            point = '-'
            color = 1

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

    def draw_text(self, x, y, text, color=0, size=FONT_SIZE, offset=None):
        if offset is None:
            offset = 0, 0
        dx, dy = offset
        x, y = x + dx, y + dy
        if not self.curses:
            font = pygame.font.SysFont('Courier', size)
            rgb = self.color_rgb(color)
            # Enable antialiasing.
            text = font.render(text, True, rgb, BLACK)
            self.screen.blit(text, (x, y))
        else:
            attr = curses.color_pair(1 + color % 7)
            try:
                self.screen.addstr(y, x, text, attr)
            except:
                pass

    def clear(self):
        if not self.curses:
            self.screen.fill(BLACK)
        else:
            self.screen.erase()

    def update(self):
        if not self.curses:
            pygame.display.update()
        else:
            self.screen.refresh()

    def wait(self):
        if not self.curses:
            while True:
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    return
        else:
            pass
