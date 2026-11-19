#!/usr/bin/env python3
"""news-image-20261119 — one image summing up the world news of
Thursday 19 November 2026.

Pure Python 3 standard library only. No network, no files read at run
time: every pixel is drawn in code, deterministically, so two runs
write byte-identical PNGs.

Layout (1024 x 1024, newspaper front page):
  masthead  : THE WORLD IN ONE DAY / THURSDAY 19 NOVEMBER 2026
  hero      : Shenzhen summit — Trump, Xi and Putin meet three-way
  row 2     : Gulf war widens (Iran hits US bases, tankers burn) |
              Gaza — Israeli tanks cross the Yellow Line
  row 3     : Anthropic debuts at $83 a share, biggest IPO ever |
              EU lends Ukraine 45 billion euros
  footer    : The Hague — world court rules on Rohingya genocide today

All six stories were verified against Reuters / AP / CNBC / Human Rights
Watch reporting on 19 November 2026 (see NEWS.md in this repository).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
NAVY = (20, 38, 74)
NAVY_D = (12, 24, 48)
RED = (176, 42, 30)
GOLD = (201, 162, 39)
SKY = (58, 110, 165)
SKY_L = (147, 190, 224)
SEA = (28, 68, 110)
SEA_D = (16, 44, 76)
SAND = (214, 196, 150)
GREY = (90, 90, 88)
WHITE = (255, 255, 255)
GREEN = (38, 110, 66)
TEAL = (18, 96, 96)
SPACE = (8, 10, 26)
CREAM2 = (232, 224, 200)
DUSK = (250, 226, 190)
BOARD = (16, 28, 20)

# ---------------------------------------------------------------- 5x7 font
# 7 rows of 5 pixels each; "#" = on. Copy is rendered in capitals only.
FONT = {
    "A": (" .###. ", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".#.#.", "..##.", ".#.#.", "####."),
}
FONT = {k: tuple(r.strip()[:5].ljust(5, ".") for r in v)
        for k, v in FONT.items()}


def _chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    return out + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)


def write_png(path, rgb, w, h):
    """Deterministic PNG: filter-0 rows, zlib level 9, fixed chunk order."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for _ in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx + dy, x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for yy in range(cy - rr, cy + rr + 1):
                for xx in range(cx - rr, cx + rr + 1):
                    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                    if rr * rr - 2 * rr <= d2 <= rr * rr:
                        self.set(xx, yy, c)

    def tri(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        for yy in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, yy, xb - xa + 1, 1, c)

    def starburst(self, cx, cy, r0, r1, n, c):
        pts = []
        for k in range(2 * n):
            r = r1 if k % 2 == 0 else r0
            a = math.pi * k / n - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        for k in range(len(pts)):
            self.tri((pts[k], pts[(k + 1) % len(pts)], (cx, cy)), c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = g[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        return self.draw_text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        lines, cur = [], ""
        for wd in s.upper().split():
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

# ------------------------------------------------------- illustrations
def _flag_us(c, x, y, w, h):
    """Stars and stripes, simplified: 7 stripes + blue canton."""
    for i in range(7):
        c.rect(x, y + i * h // 7, w, h // 7 + 1,
               RED if i % 2 == 0 else WHITE)
    c.rect(x, y, w * 2 // 5, h * 4 // 7, NAVY)
    for fy in range(4):
        for fx in range(5):
            c.set(x + 3 + fx * 5, y + 3 + fy * 4, WHITE)


def _flag_cn(c, x, y, w, h):
    c.rect(x, y, w, h, RED)
    c.starburst(x + 8, y + 7, 2, 5, 5, GOLD)
    for sx, sy in ((w - 10, 4), (w - 6, 9), (w - 10, 14), (w - 6, 18)):
        c.disc(x + sx, y + sy, 2, GOLD)


def _flag_ru(c, x, y, w, h):
    c.rect(x, y, w, h // 3 + 1, WHITE)
    c.rect(x, y + h // 3, w, h // 3 + 1, (0, 57, 166))
    c.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (213, 0, 50))


def illo_shenzhen(c, x, y, w, h):
    """Hero: Shenzhen at dusk, three flags over the skyline, APEC."""
    c.rect(x, y, w, h, DUSK)
    c.rect(x, y, w, h // 2, (252, 238, 210))
    c.disc(x + w - 140, y + 26, 16, GOLD)
    # skyline, heights as fractions of h
    base = y + h
    towers = [(0.00, 0.52, 0.09), (0.10, 0.70, 0.08), (0.19, 0.58, 0.10),
              (0.30, 0.86, 0.09), (0.40, 0.62, 0.08), (0.49, 0.76, 0.09),
              (0.59, 0.56, 0.08), (0.68, 0.84, 0.09), (0.78, 0.60, 0.08),
              (0.87, 0.72, 0.09)]
    for fx, fh, fw in towers:
        tx, tw, th = x + int(fx * w), int(fw * w), int(fh * h)
        c.rect(tx, base - th, tw, th, NAVY)
        for wy in range(base - th + 6, base - 4, 11):
            for wx in range(tx + 4, tx + tw - 4, 11):
                c.set(wx, wy, GOLD)
    # three flags on poles, left to right: US, China, Russia
    fy, fw, fh = y + 8, 52, 26
    for k, flag in enumerate((_flag_us, _flag_cn, _flag_ru)):
        fx = x + 14 + k * 68
        c.vline(fx, fy, 34, INK, 3)
        flag(c, fx + 3, fy, fw, fh)
    c.draw_text(x + w - 78, y + 10, "APEC", 2, NAVY)


def illo_gulf(c, x, y, w, h):
    """Night over Hormuz: island blast, burning tanker, US bases."""
    c.rect(x, y, w, h, NAVY_D)
    for sx, sy in ((20, 12), (70, 8), (130, 16), (200, 8), (260, 14),
                   (330, 8), (400, 14), (60, 30), (300, 26), (420, 30)):
        c.set(x + sx % w, y + sy % (h // 2), WHITE)
    c.disc(x + w - 40, y + 22, 11, CREAM2)
    c.disc(x + w - 44, y + 19, 9, NAVY_D)
    sea_y = y + h * 3 // 5
    c.rect(x, sea_y, w, y + h - sea_y, SEA)
    c.rect(x, sea_y, w, 3, SKY_L)
    for wx in range(0, w, 44):
        c.hline(x + wx, sea_y + 14, 24, SKY_L, 2)
    # Qeshm Island, left, with blast
    ix, iy = x + 40, sea_y - 22
    c.tri(((ix, iy + 22), (ix + 46, iy), (ix + 120, iy + 8)), SAND)
    c.rect(ix, iy + 8, 120, 14, SAND)
    c.draw_text(ix + 12, iy + 11, "QESHM", 1, INK)
    c.starburst(ix + 62, iy - 6, 7, 22, 8, GOLD)
    c.starburst(ix + 62, iy - 6, 3, 12, 8, RED)
    # burning tanker, centre-right
    tx, ty = x + w - 220, sea_y + 6
    c.rect(tx, ty, 120, 16, INK)
    c.rect(tx + 20, ty - 12, 26, 12, WHITE)
    c.rect(tx + 90, ty - 18, 8, 18, INK)
    c.starburst(tx + 60, ty - 22, 5, 16, 7, GOLD)
    c.starburst(tx + 60, ty - 22, 3, 9, 7, RED)
    # US bases label, bottom left
    c.draw_text(x + 12, y + h - 18, "KUWAIT . BAHRAIN - U.S. BASES HIT", 1, WHITE)


def illo_gaza(c, x, y, w, h):
    """Central Gaza: the Yellow Line, tanks on Salah al-Din road."""
    c.rect(x, y, w, h, SAND)
    # ruined blocks, left
    c.rect(x + 8, y + h - 34, 60, 34, (120, 110, 96))
    c.rect(x + 76, y + h - 24, 44, 24, (140, 130, 116))
    c.tri(((x + 8, y + h - 34), (x + 38, y + h - 52), (x + 68, y + h - 34)),
          (120, 110, 96))
    # road across the panel
    ry = y + h * 2 // 3
    c.rect(x, ry, w, 16, (70, 70, 68))
    for wx in range(6, w, 26):
        c.hline(x + wx, ry + 7, 14, WHITE, 2)
    # the Yellow Line, vertical gold band
    lx = x + int(w * 0.55)
    c.rect(lx, y, 6, h, GOLD)
    c.draw_text(lx - 74, y + 6, "YELLOW LINE", 1, INK)
    # tank crossing the line
    tx, ty = lx - 8, ry - 26
    c.rect(tx, ty + 12, 58, 12, (52, 62, 52))
    c.rect(tx + 10, ty, 30, 12, (52, 62, 52))
    c.line(tx + 40, ty + 6, tx + 66, ty + 2, (52, 62, 52), 3)
    c.disc(tx + 12, ty + 26, 4, INK)
    c.disc(tx + 30, ty + 26, 4, INK)
    c.disc(tx + 48, ty + 26, 4, INK)
    # smoke above the line
    for fx, fy, sr in ((0.62, 0.18, 7), (0.68, 0.12, 9), (0.74, 0.18, 7)):
        c.disc(x + int(fx * w), y + int(fy * h), sr, (110, 110, 108))
    # fleeing family, right
    fx = x + w - 64
    c.disc(fx, ry - 30, 5, INK)
    c.rect(fx - 4, ry - 25, 8, 18, RED)
    c.disc(fx + 18, ry - 26, 4, INK)
    c.rect(fx + 14, ry - 22, 7, 14, NAVY)


def illo_anthropic(c, x, y, w, h):
    """Market board: rising chart, $83, ANT ticker."""
    c.rect(x, y, w, h, BOARD)
    # grid
    for gy in range(y + 10, y + h - 8, 16):
        c.hline(x + 8, gy, w - 16, (34, 52, 38), 1)
    # candlesticks, rising
    bars = [(0.06, 0.62, 0.18), (0.16, 0.55, 0.24), (0.26, 0.58, 0.16),
            (0.36, 0.46, 0.22), (0.46, 0.48, 0.14), (0.56, 0.36, 0.20),
            (0.66, 0.30, 0.16), (0.76, 0.22, 0.14)]
    for fx, ftop, fh in bars:
        bx = x + int(fx * w)
        by = y + int(ftop * h)
        bh = int(fh * h)
        c.rect(bx, by, 12, bh, (46, 160, 90))
        c.vline(bx + 5, by - 6, bh + 12, (46, 160, 90), 2)
    # arrow up, right
    ax, ay = x + int(w * 0.86), y + int(h * 0.20)
    c.line(ax - 26, ay + 22, ax, ay, GOLD, 4)
    c.line(ax, ay, ax - 14, ay + 2, GOLD, 4)
    c.line(ax, ay, ax - 2, ay + 14, GOLD, 4)
    # big price
    c.draw_text(x + 12, y + 6, "$83", 4, GOLD)
    c.draw_text(x + 12, y + h - 22, "ANT - NASDAQ", 2, WHITE)


def illo_eu(c, x, y, w, h):
    """EU blue, ring of gold stars, 45 billion euros."""
    c.rect(x, y, w, h, (0, 51, 153))
    cx, cy, r = x + 64, y + h // 2, 34
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = int(cx + r * math.cos(a)), int(cy + r * math.sin(a))
        c.starburst(sx, sy, 2, 6, 5, GOLD)
    c.draw_text(x + 118, y + 10, "45", 5, GOLD)
    c.draw_text(x + 118, y + 50, "BILLION", 2, WHITE)


def illo_icj(c, x, y, w, h):
    """Peace Palace at night: columns, pediment, scales of justice."""
    c.rect(x, y, w, h, NAVY_D)
    for sx, sy in ((16, 10), (60, 20), (120, 8), (180, 16), (240, 10),
                   (300, 18), (360, 8), (30, 40), (200, 38), (340, 42)):
        c.set(x + sx % w, y + sy, WHITE)
    # palace: pediment + columns
    px, py = x + 30, y + h - 26
    c.tri(((px, py), (px + 110, py - 26), (px + 220, py)), CREAM2)
    for k in range(4):
        c.rect(px + 14 + k * 52, py - 24, 10, 24, CREAM2)
    c.rect(px, py, 220, 4, GOLD)
    # scales, right
    sx, sy = x + w - 78, y + 34
    c.vline(sx, sy - 18, 52, GOLD, 3)
    c.line(sx - 26, sy - 14, sx + 26, sy - 14, GOLD, 3)
    c.line(sx - 26, sy - 14, sx - 26, sy + 2, GOLD, 2)
    c.line(sx + 26, sy - 14, sx + 26, sy + 2, GOLD, 2)
    c.tri(((sx - 36, sy + 2), (sx - 16, sy + 2), (sx - 26, sy + 16)), GOLD)
    c.tri(((sx + 16, sy + 2), (sx + 36, sy + 2), (sx + 26, sy + 16)), GOLD)
    c.disc(sx, sy - 20, 4, GOLD)
    c.draw_text(x + w - 132, y + h - 20, "THE HAGUE", 1, SKY_L)

# ------------------------------------------------------------- layout
def panel(c, x, y, w, h, kicker, kcolor, headline, deck, illo):
    c.rect(x, y, w, h, PAPER)
    c.hline(x, y, w, INK, 3)
    c.hline(x, y + h - 3, w, INK, 3)
    c.vline(x, y, h, INK, 3)
    c.vline(x + w - 3, y, h, INK, 3)
    c.rect(x + 3, y + 3, w - 6, 26, kcolor)
    c.draw_text(x + 14, y + 10, kicker, 2, WHITE)
    lines = c.wrap(headline, 3, w - 28)[:2]
    hy = y + 38
    for ln in lines:
        c.draw_text(x + 14, hy, ln, 3, INK)
        hy += 25
    iy = hy + 4
    ih = (y + h - 38) - iy
    if ih > 10:
        illo(c, x + 6, iy, w - 12, ih)
    dlines = c.wrap(deck, 2, w - 28)[:2]
    dy = y + h - 38
    for ln in dlines:
        c.draw_text(x + 14, dy, ln, 2, GREY)
        dy += 15


def build():
    c = Canvas(W, H, PAPER)

    # ---- masthead
    c.rect(24, 24, 976, 104, NAVY)
    c.hline(24, 24, 976, GOLD, 3)
    c.hline(24, 125, 976, GOLD, 3)
    c.text_center(512, 38, "THE WORLD IN ONE DAY", 3, WHITE)
    c.text_center(512, 72, "THURSDAY 19 NOVEMBER 2026", 5, GOLD)

    # ---- hero: Shenzhen trilateral
    hx, hy, hw, hh = 24, 140, 976, 284
    c.rect(hx, hy, hw, hh, PAPER)
    c.hline(hx, hy, hw, INK, 3)
    c.hline(hx, hy + hh - 3, hw, INK, 3)
    c.vline(hx, hy, hh, INK, 3)
    c.vline(hx + hw - 3, hy, hh, INK, 3)
    c.rect(hx + 3, hy + 3, hw - 6, 30, RED)
    c.draw_text(hx + 15, hy + 11, "APEC - SHENZHEN", 2, WHITE)
    hlines = c.wrap("TRUMP, XI AND PUTIN MEET IN SHENZHEN", 4, hw - 30)[:2]
    yy = hy + 44
    for ln in hlines:
        c.draw_text(hx + 15, yy, ln, 4, INK)
        yy += 32
    illo_shenzhen(c, hx + 6, yy + 4, hw - 12, 118)
    dlines = c.wrap("FIRST EVER THREE-WAY MEETING OF THE NUCLEAR POWERS. "
                    "NUCLEAR ARMS, UKRAINE AND IRAN ON THE TABLE.",
                    2, hw - 30)[:2]
    dy = hy + hh - 36
    for ln in dlines:
        c.draw_text(hx + 15, dy, ln, 2, GREY)
        dy += 15

    # ---- row 2
    panel(c, 24, 436, 482, 200, "THE GULF - WAR AT SEA", RED,
          "GULF WAR WIDENS AGAIN",
          "IRAN HITS U.S. BASES IN KUWAIT AND BAHRAIN. "
          "TANKERS BURN IN HORMUZ.", illo_gulf)
    panel(c, 518, 436, 482, 200, "GAZA - CEASEFIRE STRAINED", NAVY,
          "TANKS CROSS GAZA'S YELLOW LINE",
          "ISRAEL'S RARE GROUND PUSH BEYOND THE LINE. "
          "FAMILIES FLEE AGAIN.", illo_gaza)

    # ---- row 3
    panel(c, 24, 648, 482, 200, "BUSINESS - AI", TEAL,
          "ANTHROPIC DEBUTS AT $83 A SHARE",
          "BIGGEST IPO EVER: $81.3 BILLION. "
          "TRADING STARTS TODAY.", illo_anthropic)
    panel(c, 518, 648, 482, 200, "EUROPE - UKRAINE", NAVY,
          "EU LENDS UKRAINE 45 BILLION EUROS",
          "KYIV PAYS BACK ONLY IF RUSSIA PAYS REPARATIONS. "
          "FOUR STATES OPT OUT.", illo_eu)

    # ---- footer: The Hague
    fx, fy, fw, fh = 24, 860, 976, 116
    c.rect(fx, fy, fw, fh, NAVY_D)
    c.hline(fx, fy, fw, GOLD, 3)
    c.hline(fx, fy + fh - 3, fw, GOLD, 3)
    c.vline(fx, fy, fh, GOLD, 3)
    c.vline(fx + fw - 3, fy, fh, GOLD, 3)
    illo_icj(c, fx + 6, fy + 6, 400, fh - 12)
    c.draw_text(fx + 430, fy + 12, "THE HAGUE", 2, GOLD)
    c.draw_text(fx + 430, fy + 32, "WORLD COURT RULES ON", 3, WHITE)
    c.draw_text(fx + 430, fy + 56, "ROHINGYA GENOCIDE", 3, WHITE)
    dlines = c.wrap("THE COURT DECIDES TODAY AFTER SEVEN YEARS. "
                    "A FIRST STATE VERDICT IS AT STAKE.",
                    2, fw - 460)[:2]
    dy = fy + 84
    for ln in dlines:
        c.draw_text(fx + 430, dy, ln, 2, (200, 205, 220))
        dy += 15
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    c = build()
    path = os.path.join(outdir, "entry.png")
    write_png(path, c.px, W, H)
    print("WROTE", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
