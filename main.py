#!/usr/bin/env python3
"""News-image entry for make.fun bounty news-image-20261126.

Draws a newspaper front page summing up the world news of
Thursday 26 November 2026, using only the Python standard library.
Writes one deterministic 1024x1024 PNG to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).

All stories were first reported on 26 November 2026 (or carried as
the day's news in that date's morning papers):
  - Gulf oil crisis: Houthis claim a strike on Saudi Arabia's Ras
    Tanura refinery; two tankers hit mines in the Strait of Hormuz;
    Brent crude jumps past $93 (Reuters).
  - Thanksgiving Day in the United States, with the 100th Macy's
    parade and about 81.5 million Americans travelling (AAA).
  - Shenzhou-24 docks at Tiangong: Pakistan's Muhammad Zeeshan Ali
    becomes the first foreign astronaut aboard China's station.
  - Bangladesh raises the garment minimum wage 36% to 17,000 taka
    after weeks of protests.
  - Israeli strike kills Hamas security chief Mohammad Abuelouf and
    his family in Gaza; the year-old ceasefire is under strain.
  - India marks 18 years since the 26/11 Mumbai attacks and
    celebrates Constitution Day.
  - Australia and Solomon Islands sign a security treaty in Canberra.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (250, 246, 236)
INK = (20, 20, 20)
RED = (166, 30, 34)
NAVY = (30, 58, 95)
GOLD = (176, 124, 18)
SKY = (178, 208, 228)
GREY = (90, 90, 90)
LIGHT_GREY = (210, 205, 190)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, "1" = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "•": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}

CHAR_W = 6  # glyph width + 1px spacing, in font units


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def wrap(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))
        self.clip = None  # (x0, y0, x1, y1) or None: clip drawing to a box

    def set(self, x, y, color):
        if self.clip is not None:
            cx0, cy0, cx1, cy1 = self.clip
            if not (cx0 <= x < cx1 and cy0 <= y < cy1):
                return
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, cy + dy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            dx = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, cy + dy, color)

    def poly(self, points, color):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(xx, y, color)

    def text(self, s, x, y, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, s, cx, y, scale, color):
        x = cx - text_width(s, scale) // 2
        return self.text(s, x, y, scale, color)


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# --------------------------------------------------------- illustrations --
def draw_refinery(cv, x, y, w, h):
    """Oil refinery by the sea, smoke rising from a struck tower."""
    cv.clip = (x, y, x + w, y + h)
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 70, y + 44, 28, (255, 214, 120))  # sun
    # smoke plume: dark puffs rising from the middle tower
    smoke = (70, 70, 70)
    for cx, cy, r in ((x + 150, y + 50, 26), (x + 172, y + 32, 30),
                      (x + 196, y + 56, 22), (x + 150, y + 76, 24),
                      (x + 210, y + 28, 18)):
        cv.circle(cx, cy, r, smoke)
    # ground
    cv.rect(x, y + h - 140, w, 140, (214, 196, 160))
    # storage tanks
    for tx in (x + 18, x + 96, x + 250):
        cv.rect(tx, y + h - 108, 62, 48, (240, 240, 235))
        cv.ellipse(tx + 31, y + h - 108, 31, 10, (200, 200, 195))
        cv.rect(tx, y + h - 60, 62, 6, INK)
    # distillation towers
    for tx, th in ((x + 178, 140), (x + 216, 164), (x + 254, 122)):
        cv.rect(tx, y + h - 60 - th, 26, th, (120, 120, 118))
        cv.rect(tx - 4, y + h - 60 - th, 34, 8, INK)
    # pipes
    cv.rect(x + 170, y + h - 84, 140, 8, (90, 90, 88))
    cv.rect(x + 170, y + h - 100, 8, 40, (90, 90, 88))
    # sea + tanker at the bottom
    cv.rect(x, y + h - 60, w, 60, (96, 140, 178))
    cv.rect(x + 40, y + h - 48, 250, 24, (40, 40, 44))
    cv.rect(x + 250, y + h - 72, 40, 24, (200, 200, 195))
    cv.rect(x + 258, y + h - 82, 10, 10, (40, 40, 44))
    cv.rect(x + 60, y + h - 36, 210, 4, WHITE)
    # flame on the struck tower
    cv.poly([(x + 186, y + h - 210), (x + 196, y + h - 234),
             (x + 206, y + h - 210)], (255, 140, 20))
    cv.poly([(x + 190, y + h - 210), (x + 196, y + h - 226),
             (x + 202, y + h - 210)], (255, 220, 60))
    cv.clip = None


def draw_balloon(cv, x, y, w, h):
    """Parade balloon over a city skyline. Fits a short wide box."""
    cv.clip = (x, y, x + w, y + h)
    cv.rect(x, y, w, h, SKY)
    # skyline along the bottom
    for bx, bh in ((x + 6, 26), (x + 52, 40), (x + 108, 30),
                   (x + 330, 36), (x + 386, 28), (x + 430, 42)):
        cv.rect(bx, y + h - bh, 42, bh, (70, 90, 120))
    cv.rect(x, y + h - 12, w, 12, (90, 110, 90))
    # balloon: striped globe, centre-left
    cx, cy, rx, ry = x + 150, y + 36, 72, 30
    cv.ellipse(cx, cy, rx, ry, (196, 40, 44))
    cv.ellipse(cx, cy, rx // 2, ry, (255, 214, 120))
    cv.ellipse(cx, cy, rx // 4, ry, (196, 40, 44))
    cv.poly([(cx - 20, cy + ry - 2), (cx + 20, cy + ry - 2),
             (cx + 8, cy + ry + 12), (cx - 8, cy + ry + 12)],
            (120, 60, 40))
    cv.line(cx - 6, cy + ry + 12, cx - 22, y + h - 12, INK)
    cv.line(cx + 6, cy + ry + 12, cx + 22, y + h - 12, INK)
    # confetti
    for px, py, c in ((x + 260, y + 14, RED), (x + 300, y + 30, GOLD),
                      (x + 380, y + 16, RED), (x + 420, y + 44, GOLD),
                      (x + 250, y + 56, NAVY), (x + 400, y + 60, RED)):
        cv.rect(px, py, 7, 7, c)
    # "100" badge, right side
    bx, by = x + w - 52, y + 36
    cv.circle(bx, by, 26, RED)
    cv.circle(bx, by, 22, WHITE)
    cv.text("100", bx - 17, by - 7, 2, RED)
    cv.clip = None


def draw_rocket(cv, x, y, w, h):
    """Rocket and space station over Earth. Fits a short wide box."""
    cv.clip = (x, y, x + w, y + h)
    cv.rect(x, y, w, h, (16, 24, 48))
    for sx, sy in ((x + 30, y + 12), (x + 90, y + 26), (x + 380, y + 14),
                   (x + 430, y + 40), (x + 200, y + 16), (x + 330, y + 56),
                   (x + 60, y + 60), (x + 450, y + 66)):
        cv.rect(sx, sy, 4, 4, WHITE)
    # Earth arc: only a thin sliver along the bottom of the banner
    cv.circle(x + w // 2, y + h + 260, 280, (52, 110, 190))
    cv.ellipse(x + w // 2 - 80, y + h - 8, 100, 14, (70, 150, 90))
    # space station, right side
    sx, sy = x + 300, y + 26
    cv.rect(sx, sy, 96, 20, (200, 200, 195))
    cv.rect(sx + 42, sy - 6, 12, 32, (160, 160, 155))
    cv.rect(sx - 48, sy + 4, 44, 11, (40, 90, 170))
    cv.rect(sx + 100, sy + 4, 44, 11, (40, 90, 170))
    cv.circle(sx + 48, sy + 10, 6, (255, 220, 60))
    # rocket, left side
    rx, ry = x + 120, y + 8
    cv.rect(rx, ry + 22, 30, 48, WHITE)
    cv.poly([(rx, ry + 22), (rx + 15, ry), (rx + 30, ry + 22)], RED)
    cv.poly([(rx, ry + 70), (rx - 14, ry + 76), (rx, ry + 62)],
            (196, 40, 44))
    cv.poly([(rx + 30, ry + 70), (rx + 44, ry + 76),
             (rx + 30, ry + 62)], (196, 40, 44))
    cv.circle(rx + 15, ry + 40, 7, SKY)
    # flame
    cv.poly([(rx + 5, ry + 70), (rx + 15, ry + 84),
             (rx + 25, ry + 70)], (255, 140, 20))
    cv.clip = None


# -------------------------------------------------------------- layout ----
def body_lines(cv, text, x, y, max_w, scale, color, leading=6):
    lines = wrap(text, max_w, scale)
    for ln in lines:
        cv.text(ln, x, y, scale, color)
        y += 7 * scale + leading
    return y


def story_block(cv, x, y, w, kicker, headline, body, kcolor=NAVY,
                hscale=3, bscale=2, leading=6):
    cv.text(kicker, x, y, 2, kcolor)
    y += 20
    for ln in wrap(headline, w, hscale):
        cv.text(ln, x, y, hscale, INK)
        y += 7 * hscale + 4
    y += 4
    return body_lines(cv, body, x, y, w, bscale, INK, leading)


def main():
    cv = Canvas(W, H, PAPER)

    # top rule + masthead
    cv.rect(0, 0, W, 10, INK)
    cv.text_center("THE WORLD TODAY", W // 2, 22, 7, INK)
    cv.text_center("THURSDAY 26 NOVEMBER 2026", W // 2, 78, 4, RED)
    cv.rect(32, 108, W - 64, 3, INK)
    cv.rect(32, 114, W - 64, 1, INK)

    # ---- hero: Gulf oil crisis --------------------------------------
    hx, hy, hw = 32, 126, 560
    cv.text("GULF OIL CRISIS", hx, hy, 2, NAVY)
    hy += 22
    for ln in wrap("HOUTHIS HIT SAUDI'S BIGGEST REFINERY", hw, 4):
        cv.text(ln, hx, hy, 4, INK)
        hy += 7 * 4 + 5
    hy += 6
    cv.text("SMOKE OVER RAS TANURA, BRENT PAST $93", hx, hy, 2, RED)
    hy += 26
    body_lines(
        cv,
        "YEMEN'S HOUTHIS SAY THEY STRUCK RAS TANURA, THE KINGDOM'S "
        "LARGEST REFINERY, AND SATELLITE IMAGES SHOW THICK BLACK SMOKE. "
        "SAUDI DEFENCES DOWNED FOUR DRONES. TWO TANKERS HIT MINES IN "
        "THE STRAIT OF HORMUZ. OIL JUMPED MORE THAN 2%.",
        hx, hy, hw, 2, INK)
    draw_refinery(cv, 620, 126, 372, 304)

    cv.rect(32, 438, W - 64, 3, INK)

    # ---- row 2: Thanksgiving + space --------------------------------
    y2 = 456
    col_w = 466
    # Thanksgiving (left): banner above the text
    draw_balloon(cv, 32, y2, col_w, 84)
    story_block(cv, 32, y2 + 92, col_w, "UNITED STATES",
                "THANKSGIVING DAY: 100TH MACY'S PARADE",
                "AMERICANS MARK THANKSGIVING ON THURSDAY 26 NOVEMBER. "
                "THE 100TH MACY'S PARADE STEPS OFF IN NEW YORK AS 81.5 "
                "MILLION PEOPLE TRAVEL.")
    # Space (right): banner above the text
    draw_rocket(cv, 526, y2, col_w, 84)
    story_block(cv, 526, y2 + 92, col_w, "SPACE",
                "FIRST FOREIGN ASTRONAUT ABOARD TIANGONG",
                "CHINA'S SHENZHOU-24 DOCKS WITH ITS SPACE STATION, "
                "CARRYING PAKISTAN'S MUHAMMAD ZEESHAN ALI, THE FIRST "
                "PAKISTANI IN ORBIT.")

    cv.rect(32, 708, W - 64, 3, INK)

    # ---- row 3: three stories ----------------------------------------
    y3 = 726
    cw = 304
    xs = (32, 360, 688)
    # Bangladesh
    cv.rect(xs[0], y3, cw, 30, NAVY)
    cv.text_center("TK 17,000  +36%", xs[0] + cw // 2, y3 + 8, 2, WHITE)
    story_block(cv, xs[0], y3 + 42, cw, "BANGLADESH",
                "GARMENT WAGE RISES AFTER PROTESTS",
                "MINIMUM WAGE UP 36% TO 17,000 TAKA AFTER WEEKS OF "
                "PROTESTS THAT SHUT FACTORIES. WORKERS SAY IT IS TOO "
                "LITTLE.", hscale=2, leading=4)
    # Gaza
    cv.rect(xs[1], y3, cw, 30, RED)
    cv.text_center("2ND IN 24 HOURS", xs[1] + cw // 2, y3 + 8, 2, WHITE)
    story_block(cv, xs[1], y3 + 42, cw, "GAZA",
                "ISRAELI STRIKE KILLS HAMAS SECURITY CHIEF",
                "AIRSTRIKE KILLS HAMAS SECURITY CHIEF MOHAMMAD ABUELOUF, "
                "HIS WIFE AND TWO CHILDREN IN GAZA CITY. CEASEFIRE UNDER "
                "STRAIN.", hscale=2, leading=4)
    # Mumbai
    cv.rect(xs[2], y3, cw, 30, GOLD)
    cv.text_center("18 YEARS ON", xs[2] + cw // 2, y3 + 8, 2, WHITE)
    story_block(cv, xs[2], y3 + 42, cw, "INDIA",
                "MUMBAI MARKS 18 YEARS SINCE 26/11",
                "INDIA REMEMBERS THE 2008 MUMBAI ATTACKS ON THEIR 18TH "
                "ANNIVERSARY AND MARKS CONSTITUTION DAY.", hscale=2,
                leading=4)
    # vertical dividers between the three columns
    cv.vline(344, y3, 200, LIGHT_GREY)
    cv.vline(672, y3, 200, LIGHT_GREY)

    # ---- ticker -------------------------------------------------------
    ty = 936
    cv.rect(0, ty, W, 64, NAVY)
    ticker = ("ALSO TODAY:  AUSTRALIA-SOLOMON ISLANDS SECURITY TREATY "
              "SIGNED  •  US READIES NEW TARIFF PLAN  •  SOORYAVANSHI, "
              "15, HITS 204 OFF 53 BALLS")
    y = ty + 10
    for ln in wrap(ticker, W - 48, 2):
        cv.text(ln, 24, y, 2, WHITE)
        y += 7 * 2 + 6

    cv.text_center("THE WORLD TODAY  •  THURSDAY 26 NOVEMBER 2026",
                   W // 2, 1008, 1, GREY)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(cv))
    print("wrote", path)


if __name__ == "__main__":
    main()
