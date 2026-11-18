#!/usr/bin/env python3
"""News front page v8 for make.fun bounty news-image-20261117.

Same 35-story front page as v2, but the "WHERE IT HAPPENED" section is now
the dark dotted world map from the user's digest model: dark panel, dotted
continents, bezier arcs between linked locations, category dots
(stories 1-3 plain, stories 4-15 numbered), small dots for briefs locations,
category legend inside. The grid story-number circles and REGION . BEAT
labels are coloured by category (bright circle, darker tint for the label).
All number text is dark ink, per the digest. The briefs list uses coloured
dots (no numbers), like the digest.
Stdlib + Pillow only, no network, deterministic.
Writes /output/entry.png (JPEG bytes, magic decides the format).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
NAVY = (22, 38, 63)
GOLD = (232, 182, 76)
RED = (176, 58, 46)
INK = (34, 34, 34)
GREY = (90, 86, 78)
CARD = (255, 255, 255)
BORDER = (216, 210, 196)
SKY = (188, 216, 232)
SEA = (61, 126, 166)
PANEL = (13, 24, 48)
DOTC = (70, 104, 159)
LBL = (143, 166, 207)
LEGTXT = (183, 200, 232)
SHZ = (201, 214, 240)
C_WAR = (255, 92, 77)
C_DIP = (255, 181, 36)
C_ECO = (49, 212, 196)
C_SOC = (160, 132, 242)
C_POL = (90, 168, 254)
C_GREY = (154, 167, 192)
PIN_INK = (16, 19, 26)
# darker tints of the category colours, for text on paper
T_WAR = (200, 40, 28)
T_DIP = (168, 106, 0)
T_ECO = (14, 132, 120)
T_SOC = (106, 79, 208)
T_POL = (37, 99, 201)

BASE = os.path.dirname(os.path.abspath(__file__))


def font(name, size):
    for p in (os.path.join(BASE, "fonts", name),
              os.path.join("/usr/share/fonts/truetype/dejavu", name)):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_TITLE = lambda s: font("DejaVuSans-Bold.ttf", s)
F_BODY = lambda s: font("DejaVuSans.ttf", s)


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, max_w, max_lines):
    """Wrap to at most max_lines; append ... only if text was cut."""
    lines = wrap(text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines, False
    out = lines[:max_lines]
    while out and fnt.getlength(out[-1] + "...") > max_w:
        out[-1] = out[-1].rsplit(" ", 1)[0] if " " in out[-1] else out[-1][:-1]
    out[-1] = out[-1] + "..."
    return out, True


def text(draw, xy, s, fnt, fill):
    draw.text(xy, s, font=fnt, fill=fill)


def center(draw, y, s, fnt, fill, cx=W // 2):
    draw.text((cx - fnt.getlength(s) / 2, y), s, font=fnt, fill=fill)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- heroes
# Text copied verbatim from v2 (commit dac7e64), including the story-13 fix.
HEROES = [
    ("UKRAINE \u00b7 WAR",
     "Kerch Bridge span falls in second day of strikes",
     "A road span drops into the strait on day two. Zelenskyy hails an "
     "\u201cunprecedented operation\u201d."),
    ("MIDDLE EAST \u00b7 WAR",
     "Iran drones target US radar in Bahrain \u2014 all intercepted",
     "Drones target the Sheikh Isa radar; all intercepted, no casualties, "
     "Bahrain and US say."),
    ("DIPLOMACY \u00b7 SUMMIT",
     "Xi, Trump and Putin to meet Thursday in Shenzhen",
     "First three-way summit confirmed for the APEC sidelines. Trump is "
     "in Manila for the Quad."),
]


def draw_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + 40, x + w, y + h], fill=SEA)
    d.ellipse([x + w - 52, y + 6, x + w - 22, y + 36], fill=(242, 201, 76))
    for tx in (x + 62, x + w - 82):
        d.rectangle([tx, y + 12, tx + 14, y + 40], fill=(70, 76, 84))
        d.rectangle([tx - 6, y + 8, tx + 20, y + 14], fill=(70, 76, 84))
    d.rectangle([x, y + 38, x + 138, y + 43], fill=(52, 58, 66))
    d.rectangle([x + 182, y + 38, x + w, y + 43], fill=(52, 58, 66))
    d.polygon([(x + 140, y + 38), (x + 180, y + 38), (x + 168, y + 54),
               (x + 148, y + 54)], fill=(52, 58, 66))
    for cx0, cx1 in ((x + 62, x + 138), (x + w - 68, x + 182)):
        d.line([cx0 + 7, y + 12, cx1, y + 38], fill=(120, 128, 136), width=2)
        d.line([cx0 + 7, y + 12, x + 4, y + 38], fill=(120, 128, 136), width=2)
    for sx, sy, r in ((x + 152, y + 28, 6), (x + 164, y + 22, 7), (x + 176, y + 30, 5)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(200, 200, 196))
    d.ellipse([x + 146, y + 50, x + 174, y + 58], fill=(220, 235, 242))


def draw_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(34, 52, 77))
    for sx, sy in ((x + 30, y + 10), (x + 90, y + 6), (x + 200, y + 8),
                   (x + 260, y + 14), (x + 150, y + 16)):
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(220, 225, 235))
    d.rectangle([x, y + 48, x + w, y + h], fill=(46, 74, 58))
    cx = x + w // 2
    d.rectangle([cx - 3, y + 30, cx + 3, y + 48], fill=(200, 205, 212))
    d.pieslice([cx - 30, y + 18, cx + 30, y + 78], 180, 360, fill=(235, 238, 242))
    d.line([cx, y + 30, cx + 22, y + 18], fill=(235, 238, 242), width=3)
    d.ellipse([cx + 18, y + 14, cx + 26, y + 22], fill=(242, 201, 76))
    for dx, dy in ((x + 48, y + 26), (x + 128, y + 14), (x + 238, y + 30)):
        d.rectangle([dx - 9, dy, dx + 9, dy + 5], fill=(20, 22, 28))
        d.line([dx - 14, dy - 3, dx + 14, dy - 3], fill=(20, 22, 28), width=2)
        d.line([dx - 14, dy + 8, dx + 14, dy + 8], fill=(20, 22, 28), width=2)
    for bx, by in ((x + 48, y + 40), (x + 128, y + 30), (x + 238, y + 44)):
        d.line([bx - 7, by, bx + 7, by], fill=(242, 201, 76), width=3)
        d.line([bx, by - 7, bx, by + 7], fill=(242, 201, 76), width=3)
        d.line([bx - 5, by - 5, bx + 5, by + 5], fill=(242, 201, 76), width=2)
        d.line([bx - 5, by + 5, bx + 5, by - 5], fill=(242, 201, 76), width=2)
    for dx, dy in ((x + 48, y + 40), (x + 128, y + 30), (x + 238, y + 44)):
        for t in range(0, 11):
            px = cx + (dx - cx) * t / 10
            py = (y + 34) + (dy - (y + 34)) * t / 10
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(242, 201, 76))


def draw_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 233, 242))
    for bx, bw, bh in ((x + 8, 44, 30), (x + 58, 30, 40), (x + 94, 52, 26),
                       (x + 152, 36, 44), (x + 194, 48, 34), (x + 248, 34, 42),
                       (x + 288, 26, 28)):
        d.rectangle([bx, y + 44 - bh, bx + bw, y + 44], fill=(120, 138, 158))
        for wy in range(y + 48 - bh, y + 40, 9):
            for wx in range(bx + 6, bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(232, 182, 76))
    d.rectangle([x, y + 44, x + w, y + h], fill=(70, 90, 70))
    for px, code in ((x + 84, "CN"), (x + 160, "US"), (x + 236, "RU")):
        d.rectangle([px, y + 16, px + 3, y + 44], fill=(60, 60, 60))
        fx, fy = px + 3, y + 16
        if code == "CN":
            d.rectangle([fx, fy, fx + 42, fy + 16], fill=(222, 41, 16))
            for sx, sy in ((fx + 8, fy + 4), (fx + 16, fy + 3), (fx + 14, fy + 8),
                           (fx + 20, fy + 7), (fx + 17, fy + 11)):
                d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 222, 0))
        elif code == "US":
            d.rectangle([fx, fy, fx + 42, fy + 16], fill=(255, 255, 255))
            for i, yy in enumerate((0, 5, 9, 14)):
                d.rectangle([fx, fy + yy, fx + 42, fy + yy + 2],
                            fill=(178, 34, 52))
            d.rectangle([fx, fy, fx + 18, fy + 8], fill=(60, 59, 110))
            for sx in range(fx + 3, fx + 17, 5):
                for sy in range(fy + 2, fy + 8, 4):
                    d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        else:
            d.rectangle([fx, fy, fx + 42, fy + 5], fill=(255, 255, 255))
            d.rectangle([fx, fy + 5, fx + 42, fy + 11], fill=(0, 57, 166))
            d.rectangle([fx, fy + 11, fx + 42, fy + 16], fill=(213, 0, 50))


HERO_DRAW = [draw_bridge, draw_radar, draw_summit]

# ---------------------------------------------------------------- grid
GRID = [
    ("ASIA \u00b7 DIPLOMACY", "Trump lands in Manila for first Quad summit in two years",
     "Thai trade deal signed; protests in Manila."),
    ("MIDDLE EAST \u00b7 ENERGY", "Iran claims more tankers struck; one hit confirmed off Oman",
     "Tanker hit confirmed; CENTCOM denies mines."),
    ("TECH \u00b7 MARKETS", "Nvidia revenue $115.8bn, up 103% \u2014 shares jump 6%",
     "Data-centre $107.6bn; Q4 guide $130bn."),
    ("AFRICA \u00b7 HEALTH", "Ebola in DR Congo passes 11,300 cases",
     "5,500+ dead; children a third of deaths."),
    ("AMERICAS \u00b7 HEALTH", "US loses measles-free status after 26 years",
     "5,412 cases in 2026, the most since 1991."),
    ("SPACE \u00b7 UPDATE", "ULA blames first stage for Vulcan failure",
     "Rocket failed minutes after liftoff on Sunday."),
    ("CLIMATE \u00b7 COP31", "COP31 split over fossil-fuel wording",
     "Drafts: \u2018transitioning away\u2019 vs \u2018phase out\u2019."),
    ("EUROPE \u00b7 POLITICS", "Serbia\u2019s students take power after 14 years of SNS rule",
     "Student List wins 140 of 250 seats."),
    ("ASIA \u00b7 POLITICS", "Mongolia\u2019s president says he will resign",
     "Denies unproven $25m bribery claim."),
    ("EUROPE \u00b7 PROTEST", "146,000 march in France over pay",
     "Unions claim 500,000+."),
    ("VATICAN \u00b7 FAITH", "Pope Leo XIV back in Rome after 12-day tour",
     "Says lung tumour \u2018entirely contained\u2019."),
    ("ASIA \u00b7 DEFENCE", "Japan scrambles jets as Russian planes breach airspace",
     "Tokyo protests after two Russian planes cross."),
]

# grid story label -> (bright circle colour, darker label tint)
GRID_COL = {
    "ASIA \u00b7 DIPLOMACY": (C_DIP, T_DIP),
    "MIDDLE EAST \u00b7 ENERGY": (C_ECO, T_ECO),
    "TECH \u00b7 MARKETS": (C_ECO, T_ECO),
    "AFRICA \u00b7 HEALTH": (C_SOC, T_SOC),
    "AMERICAS \u00b7 HEALTH": (C_SOC, T_SOC),
    "SPACE \u00b7 UPDATE": (C_ECO, T_ECO),
    "CLIMATE \u00b7 COP31": (C_DIP, T_DIP),
    "EUROPE \u00b7 POLITICS": (C_POL, T_POL),
    "ASIA \u00b7 POLITICS": (C_POL, T_POL),
    "EUROPE \u00b7 PROTEST": (C_SOC, T_SOC),
    "VATICAN \u00b7 FAITH": (C_SOC, T_SOC),
    "ASIA \u00b7 DEFENCE": (C_WAR, T_WAR),
}

# ---------------------------------------------------------------- briefs
BRIEFS = [
    "US officials allege Iran \u2018dirty bomb\u2019 plot; Iran denies it",
    "UK sanctions 8 Israeli firms building settlements",
    "Israeli settler kills woman, 72, in Jericho",
    "Five EU states plan Rwanda migrant return hub",
    "China\u2013Canada agree tariff cuts on pork and seafood",
    "Depardieu drops appeal, admits sex assault charge",
    "S&P 500 \u22121.92%, Nasdaq 100 \u22122.7% as AI worries grow",
    "California sues OpenAI; claims agents lost control 80+ times",
    "Software bug slows Chase and Zelle; FBI: not a cyberattack",
    "SpaceX catches a Starship upper stage after orbit",
    "WHO validates Eritrea\u2019s elimination of trachoma",
    "ESA\u2019s Hera shows crater-covered side of asteroid Didymos",
    "Germany beat Netherlands 5\u20130 in Nations League",
    "Alcaraz beats Tiafoe in ATP Finals opener",
    "Robertson becomes Scotland\u2019s most-capped men\u2019s player",
    "US retail sales up 0.2% in October, slowing",
    "IMF lifts South Korea 2026 growth forecast to 3.9%",
    "China\u2019s economy slows in October",
    "UN Geneva talks on banning killer robots, day 2",
    "Brent $91.67; gold up 0.63%; euro below $1.10",
]

# category colour per brief (stories 16-35), matching the map legend
BRIEF_COLS = [C_WAR, C_POL, C_WAR, C_SOC, C_ECO, C_SOC, C_ECO, C_POL,
              C_ECO, C_ECO, C_SOC, C_ECO, C_GREY, C_GREY, C_GREY,
              C_ECO, C_ECO, C_ECO, C_DIP, C_ECO]

# ---------------------------------------------------------------- map
# Coarse continent outlines as (lon, lat), written from geographic
# knowledge. The dotted rendering is forgiving; approximate is fine.
NA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
      (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
      (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
      (-79, 9), (-77, 8), (-80, 13), (-84, 16), (-87, 21), (-90, 21),
      (-91, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26),
      (-80, 32), (-76, 35), (-75, 39), (-74, 40), (-70, 42), (-68, 44),
      (-65, 44), (-60, 46), (-55, 47), (-60, 52), (-64, 58), (-68, 58),
      (-72, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68),
      (-125, 70), (-140, 70), (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-25, 70),
             (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-60, 72),
             (-58, 68)]
SA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
      (-70, -23), (-70, -30), (-71, -37), (-73, -44), (-74, -50), (-70, -54),
      (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-57, -38), (-52, -33),
      (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
      (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
      (-75, 10)]
AF = [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-5, 35), (0, 36),
      (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (32, 31), (35, 28),
      (37, 22), (39, 18), (43, 12), (48, 11), (51, 12), (51, 10), (46, 5),
      (42, 0), (40, -5), (40, -10), (36, -18), (33, -26), (28, -33),
      (20, -35), (17, -32), (15, -27), (13, -20), (12, -17), (13, -12),
      (9, -1), (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 12)]
EURASIA = [(-6, 36), (-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46),
           (-4, 48), (-2, 50), (0, 51), (3, 53), (5, 53), (8, 57), (10, 59),
           (5, 60), (5, 62), (12, 62), (18, 60), (21, 60), (24, 58),
           (28, 60), (30, 62), (33, 67), (40, 68), (48, 68), (55, 70),
           (65, 72), (75, 73), (85, 75), (100, 77), (110, 74), (120, 73),
           (130, 72), (140, 72), (150, 70), (160, 69), (170, 66), (178, 65),
           (170, 60), (162, 56), (158, 52), (150, 60), (142, 55), (140, 45),
           (135, 43), (130, 42), (127, 40), (126, 38), (122, 32), (120, 28),
           (115, 22), (110, 20), (108, 18), (105, 10), (103, 7), (100, 8),
           (98, 10), (95, 15), (92, 21), (89, 22), (86, 20), (82, 16),
           (80, 13), (77, 8), (75, 10), (72, 20), (68, 23), (66, 25),
           (62, 25), (58, 26), (56, 26), (59, 22), (55, 17), (52, 15),
           (48, 14), (45, 13), (43, 12), (42, 15), (40, 18), (39, 21),
           (38, 24), (37, 27), (36, 29), (35, 32), (36, 36), (33, 36),
           (30, 36), (27, 37), (26, 38), (23, 36), (22, 37), (20, 39),
           (19, 42), (16, 40), (16, 38), (15, 38), (14, 41), (12, 42),
           (10, 44), (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
IRELAND = [(-10, 52), (-8, 51), (-6, 52), (-6, 54), (-8, 55), (-10, 54)]
ICELAND = [(-22, 64), (-18, 63), (-14, 64), (-15, 66), (-20, 66), (-24, 65)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (140, 36),
         (141, 39), (141, 41), (142, 43), (144, 44), (143, 42), (141, 39),
         (139, 38), (137, 37), (135, 35), (132, 34), (130, 33)]
SUMATRA = [(95, 5), (97, 3), (100, 0), (103, -3), (105, -5), (104, -6),
           (102, -4), (100, 0), (97, 4)]
BORNEO = [(109, 1), (110, 2), (113, 4), (117, 6), (119, 1), (117, -2),
          (114, -3), (110, -3), (109, 0)]
JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
        (106, -7)]
SULAWESI = [(119, 0), (120, -1), (121, -2), (123, 0), (120, 1)]
NEWGUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8),
             (147, -9), (142, -8), (138, -7), (134, -4), (131, -2)]
PHILIPPINES = [(120, 18), (121, 16), (122, 14), (124, 11), (122, 10),
               (120, 13), (120, 16)]
SRILANKA = [(80, 9), (81, 8), (80, 6), (79, 8)]
TAIWAN = [(120, 23), (121, 24), (122, 25), (121, 23)]
NZ_N = [(174, -37), (176, -38), (178, -38), (176, -40), (174, -42),
        (172, -41), (174, -39)]
NZ_S = [(167, -45), (169, -43), (172, -41), (174, -40), (172, -42),
        (169, -44), (167, -46)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
              (44, -25), (43, -21), (43, -17)]
AU = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
      (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
      (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
      (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
      (118, -20), (114, -22)]
TASMANIA = [(145, -41), (148, -41), (148, -43), (146, -43)]
LAND = [NA, GREENLAND, SA, AF, EURASIA, UK, IRELAND, ICELAND, JAPAN,
        SUMATRA, BORNEO, JAVA, SULAWESI, NEWGUINEA, PHILIPPINES, SRILANKA,
        TAIWAN, NZ_N, NZ_S, MADAGASCAR, AU, TASMANIA]
HOLES = [
    [(28, 44), (30, 45), (33, 46), (36, 46), (39, 45), (41, 43), (41, 41),
     (38, 41), (35, 41), (32, 41), (30, 42), (28, 43)],
    [(47, 47), (50, 47), (53, 45), (54, 42), (53, 39), (51, 37), (49, 37),
     (47, 39), (46, 42), (47, 45)],
    [(-92, 48), (-88, 48), (-85, 46), (-82, 44), (-79, 43), (-76, 44),
     (-79, 45), (-84, 46), (-88, 47), (-91, 47)],
    [(-6, 36), (0, 38), (3, 39), (6, 38), (8, 39), (10, 38), (12, 40),
     (15, 40), (16, 38), (18, 40), (19, 39), (20, 38), (22, 37), (23, 36),
     (26, 36), (28, 36), (30, 36), (33, 36), (36, 36), (36, 34), (33, 33),
     (30, 32), (28, 32), (25, 32), (22, 33), (20, 32), (18, 32), (15, 32),
     (12, 33), (11, 34), (10, 37), (8, 37), (6, 37), (3, 37), (0, 36),
     (-2, 36), (-5, 36)],
    [(-78, 55), (-82, 55), (-85, 58), (-87, 60), (-85, 62), (-80, 62),
     (-78, 58)],
]

# (story number, lon, lat, category colour)
PINS = [(1, 36.5, 45.3, C_WAR), (2, 50.5, 26.2, C_WAR),
        (3, 114.1, 22.5, C_DIP), (4, 121.0, 14.6, C_DIP),
        (5, 59.5, 24.0, C_ECO), (6, -121.9, 37.4, C_ECO),
        (7, 23.0, -3.0, C_SOC), (8, -100.0, 39.0, C_SOC),
        (9, -80.5, 28.4, C_ECO), (10, 30.7, 36.9, C_DIP),
        (11, 22.5, 45.2, C_POL), (12, 106.9, 47.9, C_POL),
        (13, 2.35, 48.85, C_SOC), (14, 12.5, 41.0, C_SOC),
        (15, 140.0, 38.0, C_WAR)]
# small dots for briefs locations: (lon, lat, colour)
BDOTS = [(51.4, 35.7, C_WAR), (30.1, -1.9, C_SOC), (-75.7, 45.4, C_ECO),
         (127.0, 37.5, C_ECO), (13.4, 52.5, C_GREY), (38.9, 15.3, C_SOC)]
# arcs between genuinely linked locations: (lon1, lat1, lon2, lat2, colour, lift, side)
# side = sideways bulge as a fraction of the segment length (perpendicular);
# used for the near-vertical Tehran->Bahrain arc, which a north lift hides.
ARCS = [((37.6, 55.8), (114.1, 22.5), C_DIP, 0.16, 0),
        ((121.0, 14.6), (114.1, 22.5), C_DIP, 0.9, 0),
        ((51.4, 35.7), (50.5, 26.2), C_WAR, 0, 0.8),
        ((4.4, 50.8), (30.1, -1.9), C_SOC, 0.2, 0)]
LEGEND = [("Conflict", C_WAR), ("Diplomacy", C_DIP), ("Economy", C_ECO),
          ("Society", C_SOC), ("Politics", C_POL)]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    truncated = []

    # ---- masthead
    d.rectangle([0, 0, W, 96], fill=NAVY)
    center(d, 8, "THE WORLD IN ONE DAY", F_TITLE(28), (255, 255, 255))
    center(d, 44, "Tuesday 17 November 2026", F_TITLE(42), GOLD)
    d.rectangle([40, 93, W - 40, 95], fill=GOLD)

    # ---- heroes
    hy, hh, hw, gap = 104, 160, 320, 16
    for i, (kicker, head, summ) in enumerate(HEROES):
        x = 16 + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=BORDER, width=1)
        HERO_DRAW[i](d, x + 1, hy + 1, hw - 2, 60)
        ty = hy + 68
        text(d, (x + 10, ty), kicker, F_TITLE(12), RED)
        hl, cut = fit_lines(head, F_TITLE(19), hw - 20, 2)
        if cut:
            truncated.append("hero head %d" % (i + 1))
        yy = ty + 18
        for ln in hl:
            text(d, (x + 10, yy), ln, F_TITLE(19), NAVY)
            yy += 22
        sl, cut = fit_lines(summ, F_BODY(12), hw - 20, 2)
        if cut:
            truncated.append("hero summ %d" % (i + 1))
        for ln in sl:
            text(d, (x + 10, yy), ln, F_BODY(12), INK)
            yy += 14

    # ---- grid header
    gy = 274
    text(d, (16, gy), "MORE OF THE DAY", F_TITLE(16), NAVY)
    lbl = "STORIES 4\u201315"
    lw = F_TITLE(12).getlength(lbl)
    d.rectangle([196, gy + 9, W - 16, gy + 11], fill=RED)
    d.rectangle([W - 16 - lw - 8, gy - 2, W - 16, gy + 16], fill=PAPER)
    text(d, (W - 16 - lw, gy + 2), lbl, F_TITLE(12), GREY)

    # ---- grid 3 x 4
    gy0, cw, ch, cg = 292, 320, 62, 16
    for i, (label, head, summ) in enumerate(GRID):
        r, c = divmod(i, 3)
        x = 16 + c * (cw + cg)
        y = gy0 + r * (ch + 2)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=BORDER, width=1)
        n = str(i + 4)
        col, tint = GRID_COL[label]
        d.ellipse([x + 8, y + 7, x + 28, y + 27], fill=col)
        nf = F_TITLE(12)
        d.text((x + 18 - nf.getlength(n) / 2, y + 10), n, font=nf,
               fill=PIN_INK)
        text(d, (x + 34, y + 6), label, F_TITLE(11), tint)
        hl, cut = fit_lines(head, F_TITLE(14), cw - 42, 2)
        if cut:
            truncated.append("grid head %d" % (i + 4))
        yy = y + 17
        for ln in hl:
            text(d, (x + 34, yy), ln, F_TITLE(14), NAVY)
            yy += 15
        sl, cut = fit_lines(summ, F_BODY(11), cw - 42, 1)
        if cut:
            truncated.append("grid summ %d" % (i + 4))
        sy = y + 32 if len(hl) == 1 else y + 48
        for ln in sl:
            text(d, (x + 34, sy), ln, F_BODY(11), GREY)
            sy += 13

    # ---- map header
    my = 556
    text(d, (16, my), "WHERE IT HAPPENED", F_TITLE(16), NAVY)
    d.rectangle([216, my + 9, W - 16, my + 11], fill=RED)

    # ---- dark dotted map panel (digest model)
    mx0, my0, mx1, my1 = 16, 574, W - 16, 846
    d.rounded_rectangle([mx0, my0, mx1, my1], radius=8, fill=PANEL)
    K = 2.25
    TOP = 70
    MW, MH = int(350 * K), int(110 * K)
    PX0 = mx0 + (mx1 - mx0 - MW) // 2
    PY0 = my0 + 22

    def px(lon, lat):
        return (PX0 + (lon + 170) * K, PY0 + (TOP - lat) * K)

    # legend inside the panel
    lf = F_TITLE(12)
    items = []
    for lab, col in LEGEND:
        items.append((lf.getlength(lab), lab, col))
    total = sum(w + 13 for w, _, _ in items) + 4 * 14
    kx = mx1 - 16 - total
    for w, lab, col in items:
        d.ellipse([kx, my0 + 14, kx + 8, my0 + 22], fill=col)
        text(d, (kx + 13, my0 + 12), lab, lf, LEGTXT)
        kx += w + 13 + 14

    # dotted continents from a land mask
    mask = Image.new("L", (MW + 8, MH + 8), 0)
    md = ImageDraw.Draw(mask)
    for pts in LAND:
        md.polygon([((lo + 170) * K, (TOP - la) * K) for lo, la in pts], fill=255)
    for pts in HOLES:
        md.polygon([((lo + 170) * K, (TOP - la) * K) for lo, la in pts], fill=0)
    STEP = 6
    for j in range(0, MH, STEP):
        for i in range(0, MW, STEP):
            if mask.getpixel((i + STEP // 2, j + STEP // 2)) > 128:
                cx_, cy_ = PX0 + i + STEP // 2, PY0 + j + STEP // 2
                d.ellipse([cx_ - 1.5, cy_ - 1.5, cx_ + 1.5, cy_ + 1.5], fill=DOTC)

    def bez(p0, p1, lift, side=0, n=40):
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        dist = math.hypot(dx, dy)
        c = (mx - dy * side, my - lift * dist + dx * side)
        pts = []
        for k in range(n + 1):
            t = k / n
            pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1]))
        return pts

    def arc_line(a, b, col, lift, side=0):
        flat = [v for p in bez(a, b, lift, side) for v in p]
        d.line(flat, fill=mix(PANEL, col, 0.35), width=5, joint="curve")
        d.line(flat, fill=col, width=2, joint="curve")

    for (lo1, la1), (lo2, la2), col, lift, side in ARCS:
        arc_line(px(lo1, la1), px(lo2, la2), col, lift, side)

    def dot(p, col, r=4):
        d.ellipse([p[0] - r - 3, p[1] - r - 3, p[0] + r + 3, p[1] + r + 3],
                  fill=mix(PANEL, col, 0.3))
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col,
                  outline=(255, 255, 255), width=1)

    for lo, la, col in BDOTS:
        dot(px(lo, la), col)

    def pin(p, n, col, r=9):
        d.ellipse([p[0] - r - 4, p[1] - r - 4, p[0] + r + 4, p[1] + r + 4],
                  fill=mix(PANEL, col, 0.28))
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col,
                  outline=(255, 255, 255), width=2)
        if n >= 4:
            # numbered for grid stories only; heroes (1-3) stay plain dots
            s = str(n)
            nf = F_TITLE(10)
            d.text((p[0] - nf.getlength(s) / 2, p[1] - 5), s, font=nf,
                   fill=PIN_INK)

    for n, lo, la, col in PINS:
        pin(px(lo, la), n, col)
    sx, sy = px(114.1, 22.5)
    lab = "Shenzhen"
    lf2 = F_TITLE(11)
    text(d, (sx - 8 - lf2.getlength(lab), sy + 12), lab, lf2, SHZ)

    # ---- briefs
    by = 854
    text(d, (16, by), "ALSO ON TUESDAY 17 NOVEMBER", F_TITLE(16), NAVY)
    d.rectangle([316, by + 9, W - 16, by + 11], fill=RED)
    bf = F_BODY(12)
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, 10)
        x = 16 + col * 496
        y = 870 + row * 11
        # coloured dot only, no number (like the user's digest file)
        d.ellipse([x, y + 1, x + 8, y + 9], fill=BRIEF_COLS[i])
        bx = x + 14
        s = b
        if bf.getlength(s) > 496 - 14 - 4:
            while bf.getlength(s) > 496 - 14 - 4 and len(s) > 20:
                s = s[:-4] + "..."
            truncated.append("brief %d" % (i + 16))
        text(d, (bx, y), s, bf, INK)

    # ---- footer
    d.rectangle([16, 991, W - 16, 992], fill=BORDER)
    text(d, (16, 997), "Sources: Reuters \u00b7 AP \u00b7 Al Jazeera \u00b7 CNN \u00b7 CNBC \u00b7 WHO \u00b7 PAHO \u00b7 UKMTO \u00b7 Just Security \u00b7 UN News",
         F_BODY(11), GREY)
    text(d, (16, 1008), "Every story happened or was first reported on Tuesday 17 November 2026. Disputed claims are attributed.",
         F_BODY(11), GREY)
    return img, truncated


def main():
    out = "/output/entry.png"
    os.makedirs("/output", exist_ok=True)
    img, truncated = build()
    img.save(out, "JPEG", quality=60, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
    print("truncated:", truncated if truncated else "none")


if __name__ == "__main__":
    main()
