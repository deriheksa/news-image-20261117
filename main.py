#!/usr/bin/env python3
"""News front page for make.fun bounty news-image-20261117.

Draws a dense newspaper front page summing up Tuesday 17 November 2026:
masthead -> 3 hero stories with flat illustrations -> 12 numbered grid
stories -> world map with numbered dots -> 20 briefs -> sources footer.
35 stories total. Stdlib + Pillow only, no network, deterministic.
Writes /output/entry.png (JPEG bytes, magic decides the format).
"""
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
MAP_BG = (232, 238, 242)
LAND = (195, 213, 224)

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


# ---------------------------------------------------------------- heroes
HEROES = [
    ("UKRAINE · WAR",
     "Kerch Bridge span falls in second day of strikes",
     "A road span drops into the strait on day two. Zelenskyy hails an "
     "\u201cunprecedented operation\u201d."),
    ("MIDDLE EAST · WAR",
     "Iran drones target US radar in Bahrain \u2014 all intercepted",
     "Drones target the Sheikh Isa radar; all intercepted, no casualties, "
     "Bahrain and US say."),
    ("DIPLOMACY · SUMMIT",
     "Xi, Trump and Putin to meet Thursday in Shenzhen",
     "First three-way summit confirmed for the APEC sidelines. Trump is "
     "in Manila for the Quad."),
]


def draw_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=SEA)
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(242, 201, 76))
    for tx in (x + 62, x + w - 82):
        d.rectangle([tx, y + 18, tx + 14, y + h * 0.66], fill=(70, 76, 84))
        d.rectangle([tx - 6, y + 12, tx + 20, y + 20], fill=(70, 76, 84))
    d.rectangle([x, y + 62, x + 138, y + 70], fill=(52, 58, 66))
    d.rectangle([x + 182, y + 62, x + w, y + 70], fill=(52, 58, 66))
    d.polygon([(x + 140, y + 62), (x + 180, y + 62), (x + 168, y + 92),
               (x + 148, y + 92)], fill=(52, 58, 66))
    for cx0, cx1 in ((x + 62, x + 138), (x + w - 68, x + 182)):
        d.line([cx0 + 7, y + 16, cx1, y + 62], fill=(120, 128, 136), width=2)
        d.line([cx0 + 7, y + 16, x + 4, y + 62], fill=(120, 128, 136), width=2)
    for sx, sy, r in ((x + 152, y + 44, 7), (x + 164, y + 36, 9), (x + 176, y + 46, 6)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(200, 200, 196))
    d.ellipse([x + 146, y + 86, x + 174, y + 98], fill=(220, 235, 242))


def draw_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(34, 52, 77))
    for sx, sy in ((x + 30, y + 14), (x + 90, y + 8), (x + 200, y + 12),
                   (x + 260, y + 20), (x + 150, y + 22)):
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(220, 225, 235))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(46, 74, 58))
    cx = x + w // 2
    d.rectangle([cx - 4, y + 46, cx + 4, y + h - 18], fill=(200, 205, 212))
    d.pieslice([cx - 34, y + 46, cx + 34, y + 114], 180, 360, fill=(235, 238, 242))
    d.line([cx, y + 46, cx + 26, y + 30], fill=(235, 238, 242), width=3)
    d.ellipse([cx + 22, y + 26, cx + 30, y + 34], fill=(242, 201, 76))
    for dx, dy in ((x + 48, y + 26), (x + 128, y + 14), (x + 238, y + 30)):
        d.rectangle([dx - 9, dy, dx + 9, dy + 5], fill=(20, 22, 28))
        d.line([dx - 14, dy - 3, dx + 14, dy - 3], fill=(20, 22, 28), width=2)
        d.line([dx - 14, dy + 8, dx + 14, dy + 8], fill=(20, 22, 28), width=2)
    for bx, by in ((x + 48, y + 44), (x + 128, y + 32), (x + 238, y + 48)):
        d.line([bx - 7, by, bx + 7, by], fill=(242, 201, 76), width=3)
        d.line([bx, by - 7, bx, by + 7], fill=(242, 201, 76), width=3)
        d.line([bx - 5, by - 5, bx + 5, by + 5], fill=(242, 201, 76), width=2)
        d.line([bx - 5, by + 5, bx + 5, by - 5], fill=(242, 201, 76), width=2)
    for dx, dy in ((x + 48, y + 44), (x + 128, y + 32), (x + 238, y + 48)):
        for t in range(0, 11):
            px = cx + (dx - cx) * t / 10
            py = (y + 52) + (dy - (y + 52)) * t / 10
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(242, 201, 76))


def draw_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 233, 242))
    for bx, bw, bh in ((x + 8, 44, 46), (x + 58, 30, 62), (x + 94, 52, 40),
                       (x + 152, 36, 70), (x + 194, 48, 52), (x + 248, 34, 66),
                       (x + 288, 26, 44)):
        d.rectangle([bx, y + h - 26 - bh, bx + bw, y + h - 26], fill=(120, 138, 158))
        for wy in range(y + h - 22 - bh, y + h - 30, 10):
            for wx in range(bx + 6, bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(232, 182, 76))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(70, 90, 70))
    for px, code in ((x + 84, "CN"), (x + 160, "US"), (x + 236, "RU")):
        d.rectangle([px, y + 30, px + 3, y + h - 26], fill=(60, 60, 60))
        fx, fy = px + 3, y + 30
        if code == "CN":
            d.rectangle([fx, fy, fx + 42, fy + 26], fill=(222, 41, 16))
            for sx, sy in ((fx + 8, fy + 6), (fx + 16, fy + 5), (fx + 14, fy + 12),
                           (fx + 20, fy + 10), (fx + 17, fy + 17)):
                d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 222, 0))
        elif code == "US":
            for i in range(7):
                d.rectangle([fx, fy + i * 4, fx + 42, fy + i * 4 + 2],
                            fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
            d.rectangle([fx, fy, fx + 18, fy + 14], fill=(60, 59, 110))
            for sx in range(fx + 3, fx + 17, 5):
                for sy in range(fy + 3, fy + 13, 5):
                    d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        else:
            d.rectangle([fx, fy, fx + 42, fy + 9], fill=(255, 255, 255))
            d.rectangle([fx, fy + 9, fx + 42, fy + 18], fill=(0, 57, 166))
            d.rectangle([fx, fy + 18, fx + 42, fy + 26], fill=(213, 0, 50))


HERO_DRAW = [draw_bridge, draw_radar, draw_summit]

# ---------------------------------------------------------------- grid
GRID = [
    ("ASIA · DIPLOMACY", "Trump lands in Manila for first Quad summit in two years",
     "Thai trade deal signed; protests in Manila."),
    ("MIDDLE EAST · ENERGY", "Iran claims more tankers struck; one hit confirmed off Oman",
     "Tanker hit confirmed; CENTCOM denies mines."),
    ("TECH · MARKETS", "Nvidia revenue $115.8bn, up 103% \u2014 shares jump 6%",
     "Data-centre $107.6bn; Q4 guide $130bn."),
    ("AFRICA · HEALTH", "Ebola in DR Congo passes 11,300 cases",
     "5,500+ dead; children a third of deaths."),
    ("AMERICAS · HEALTH", "US loses measles-free status after 26 years",
     "5,412 cases in 2026, the most since 1991."),
    ("SPACE · UPDATE", "ULA blames first stage for Vulcan failure",
     "Rocket failed minutes after liftoff on Sunday."),
    ("CLIMATE · COP31", "COP31 split over fossil-fuel wording",
     "Drafts: \u2018transitioning away\u2019 vs \u2018phase out\u2019."),
    ("EUROPE · POLITICS", "Serbia\u2019s students take power after 14 years of SNS rule",
     "Student List wins 140 of 250 seats."),
    ("ASIA · POLITICS", "Mongolia\u2019s president says he will resign",
     "Denies unproven $25m bribery claim."),
    ("EUROPE · PROTEST", "146,000 march in France over pay",
     "Unions claim 500,000+."),
    ("VATICAN · FAITH", "Pope Leo XIV back in Rome after 12-day tour",
     "Says lung tumour \u2018entirely contained\u2019."),
    ("ASIA · DEFENCE", "Japan scrambles jets as Russian planes breach airspace",
     "Tokyo protests after two Russian planes cross."),
]

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

# ---------------------------------------------------------------- map
NA = [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
      (-55, 47), (-70, 42), (-75, 35), (-80, 25), (-90, 20), (-105, 20),
      (-115, 30), (-125, 40), (-150, 60)]
SA = [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
      (-60, -40), (-70, -50), (-75, -35), (-80, -20)]
EU = [(-10, 36), (-10, 43), (-5, 48), (0, 50), (5, 55), (10, 58), (18, 60),
      (25, 70), (30, 68), (35, 60), (30, 55), (28, 45), (20, 40), (12, 44),
      (5, 43), (-2, 37)]
AF = [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
      (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -30),
      (20, -35), (15, -30), (12, -18), (8, -2), (9, 4), (-8, 5)]
AS = [(35, 68), (50, 70), (70, 72), (90, 75), (110, 75), (130, 72), (150, 70),
      (170, 66), (180, 65), (170, 60), (160, 55), (140, 45), (130, 40),
      (127, 35), (120, 30), (110, 20), (105, 10), (100, 5), (95, 15),
      (90, 22), (80, 10), (75, 8), (70, 20), (60, 25), (55, 28), (50, 30),
      (45, 35), (40, 36), (35, 40), (35, 60)]
AU = [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
      (153, -27), (146, -19), (142, -11), (136, -12), (130, -13), (122, -14)]
CONTINENTS = [NA, SA, EU, AF, AS, AU]

# (story number, lon, lat)
DOTS = [(1, 36.5, 45.3), (2, 50.5, 26.2), (3, 114.1, 22.5), (4, 121.0, 14.6),
        (5, 57.5, 27.5), (7, 23.0, -3.0), (8, -100.0, 39.0), (9, -80.5, 28.4),
        (10, 30.7, 36.9), (11, 20.5, 44.8), (12, 106.9, 47.9),
        (13, 2.35, 48.85), (14, 12.5, 41.9), (15, 140.0, 38.0)]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    truncated = []

    # ---- masthead
    d.rectangle([0, 0, W, 112], fill=NAVY)
    center(d, 12, "THE WORLD IN ONE DAY", F_TITLE(34), (255, 255, 255))
    center(d, 52, "Tuesday 17 November 2026", F_TITLE(50), GOLD)
    d.rectangle([40, 108, W - 40, 110], fill=GOLD)

    # ---- heroes
    hy, hh, hw, gap = 122, 200, 320, 16
    for i, (kicker, head, summ) in enumerate(HEROES):
        x = 16 + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=BORDER, width=1)
        HERO_DRAW[i](d, x + 1, hy + 1, hw - 2, 96)
        ty = hy + 104
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
            yy += 15

    # ---- grid header
    gy = 334
    text(d, (16, gy), "MORE OF THE DAY", F_TITLE(16), NAVY)
    lbl = "STORIES 4\u201315"
    lw = F_TITLE(12).getlength(lbl)
    d.rectangle([196, gy + 9, W - 16, gy + 11], fill=RED)
    d.rectangle([W - 16 - lw - 8, gy - 2, W - 16, gy + 16], fill=PAPER)
    text(d, (W - 16 - lw, gy + 2), lbl, F_TITLE(12), GREY)

    # ---- grid 3 x 4
    gy0, cw, ch, cg = 354, 320, 68, 16
    for i, (label, head, summ) in enumerate(GRID):
        r, c = divmod(i, 3)
        x = 16 + c * (cw + cg)
        y = gy0 + r * (ch + 4)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=BORDER, width=1)
        n = str(i + 4)
        d.ellipse([x + 8, y + 8, x + 28, y + 28], fill=RED)
        nf = F_TITLE(13)
        d.text((x + 18 - nf.getlength(n) / 2, y + 10), n, font=nf, fill=(255, 255, 255))
        text(d, (x + 34, y + 7), label, F_TITLE(11), RED)
        hl, cut = fit_lines(head, F_TITLE(15), cw - 42, 2)
        if cut:
            truncated.append("grid head %d" % (i + 4))
        yy = y + 22
        for ln in hl:
            text(d, (x + 34, yy), ln, F_TITLE(15), NAVY)
            yy += 17
        sl, cut = fit_lines(summ, F_BODY(12), cw - 42, 1)
        if cut:
            truncated.append("grid summ %d" % (i + 4))
        sy = y + 22 + (17 if len(hl) == 1 else 34)
        for ln in sl:
            text(d, (x + 34, sy), ln, F_BODY(12), GREY)
            sy += 14

    # ---- map (lon 2.33 px/deg centred, lat 1.164 px/deg; lat clamped 70..-52)
    my = 643
    text(d, (16, my), "WHERE IT HAPPENED", F_TITLE(16), NAVY)
    d.rectangle([216, my + 9, W - 16, my + 11], fill=RED)
    mx0, my0, mx1, my1 = 16, 661, W - 16, 811
    d.rectangle([mx0, my0, mx1, my1], fill=MAP_BG, outline=BORDER, width=1)
    lon0 = mx0 + (mx1 - mx0 - 360 * 2.33) / 2.0

    def proj(lon, lat):
        lat = max(-52.0, min(70.0, lat))
        return (lon0 + (lon + 170) * 2.33,
                my0 + 4 + (70 - lat) * (my1 - my0 - 8) / 122.0)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(255, 255, 255))
    nf = F_TITLE(10)
    for num, lon, lat in DOTS:
        px, py = proj(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        s = str(num)
        d.text((px - nf.getlength(s) / 2, py - 6), s, font=nf, fill=(255, 255, 255))

    # ---- briefs
    by = 819
    text(d, (16, by), "ALSO ON TUESDAY 17 NOVEMBER", F_TITLE(16), NAVY)
    d.rectangle([316, by + 9, W - 16, by + 11], fill=RED)
    bf, bnf = F_BODY(13), F_TITLE(13)
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, 10)
        x = 16 + col * 496
        y = 841 + row * 13
        num = "%d." % (i + 16)
        text(d, (x, y), num, bnf, RED)
        bx = x + bnf.getlength(num) + 4
        s = b
        if bf.getlength(s) > 496 - (bx - x) - 4:
            while bf.getlength(s) > 496 - (bx - x) - 4 and len(s) > 20:
                s = s[:-4] + "..."
            truncated.append("brief %d" % (i + 16))
        text(d, (bx, y), s, bf, INK)

    # ---- footer
    d.rectangle([16, 974, W - 16, 975], fill=BORDER)
    text(d, (16, 982), "Sources: Reuters \u00b7 AP \u00b7 Al Jazeera \u00b7 CNN \u00b7 CNBC \u00b7 WHO \u00b7 PAHO \u00b7 UKMTO \u00b7 Just Security \u00b7 UN News",
         F_BODY(11), GREY)
    text(d, (16, 998), "Every story happened or was first reported on Tuesday 17 November 2026. Disputed claims are attributed.",
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
