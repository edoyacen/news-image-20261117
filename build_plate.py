# -*- coding: utf-8 -*-
"""Draw the plate for Tuesday 17 November 2026 and write it as one 1024x1024 page.

The page is one front page for the day: three drawn lead stories, a strip of the day's
numbers, twelve story cards, a world map with one numbered pin per brief at that story's real
longitude and latitude, the briefs themselves, and a footer that names the sources. Every text
run is measured with the real font metrics before it is placed, so a line that cannot fit is
shorter, never clipped and never overlapping; the map is projected from lon/lat, so a pin is
where the story was.

Run it, then render plate.html:

    python3 build_plate.py
"""
import io
import math

from PIL import ImageFont

GEORGIA = "C:/Windows/Fonts/georgia.ttf"
GEORGIA_B = "C:/Windows/Fonts/georgiab.ttf"
ARIAL = "C:/Windows/Fonts/arial.ttf"
ARIAL_B = "C:/Windows/Fonts/arialbd.ttf"

_FONTS = {}


def font(path, size):
    """One TrueType face at one size, cached: measuring is the hot path of this program."""
    key = (path, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, size)
    return _FONTS[key]


def width(text, path=ARIAL, size=12):
    """The width of a text run in CSS pixels, as the browser lays it out."""
    return font(path, size).getlength(text)


def wrap(text, max_width, path=ARIAL, size=12):
    """The words of a run, broken into the lines that fit a box."""
    lines, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if width(candidate, path, size) > max_width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def clip(text, max_width, path=ARIAL, size=12):
    """A run cut to a box with an ellipsis, for the one-line briefs on the map's right."""
    out = text
    while out and width(out + "\u2026", path, size) > max_width:
        out = out[:-1]
    return out + "\u2026" if out != text else text


# --------------------------------------------------------------------- the day
LEADS = [
    dict(
        region="EUROPE \u00b7 CRIMEA",
        colour="#1a66c2",
        title="Ukraine brings down the span of the Crimea bridge",
        blurb="A missile and drone attack weeks in the planning cuts the road bridge Russia built to "
              "the peninsula. Zelensky calls it \u201cunprecedented\u201d; Moscow answers on Kyiv\u2019s bridges.",
        scene="bridge",
        band="KERCH \u00b7 THE SPAN IS DOWN",
        sub="MOSCOW HITS KYIV\u2019S BRIDGES IN RETURN",
    ),
    dict(
        region="BUSINESS \u00b7 AI",
        colour="#c86a28",
        title="Nvidia doubles revenue and rules out Huang\u2019s return",
        blurb="The board opens the call by saying the ousted chief executive will not be reinstated. "
              "He will testify to Congress on a \u201cpotential breach of national security\u201d.",
        scene="chip",
        band="SANTA CLARA \u00b7 NO HUANG",
        sub="AND A CONGRESSIONAL HEARING AHEAD",
    ),
    dict(
        region="HEALTH \u00b7 AMERICAS",
        colour="#b3402e",
        title="America loses its measles-free status after 26 years",
        blurb="More than 5,400 cases and 10 deaths this year: the first time the disease has spread "
              "continually in the United States since the early 1990s.",
        scene="measles",
        band="WASHINGTON \u00b7 26 YEARS GONE",
        sub="5,400 CASES \u00b7 10 DEATHS THIS YEAR",
    ),
]

NUMBERS = [
    ("5,400", "measles cases in the US\nand 10 deaths this year"),
    ("28%", "of Pakistan\u2019s electricity\nis now solar, up from 1%"),
    ("46", "injured when two trains\ncollided in Prague"),
    ("200+", "jailed in Guinea over\nillegal gold mining"),
    ("$41m", "Beckham sues Coty over\ncut-price fragrance sales"),
    ("1,605", "pesticide poisoning\nreports in Brazil"),
]

CARDS = [
    ("MIDDLE EAST", "IRAN \u00b7 WAR", "#b3402e", "Iran and the US trade fire again",
     "Tehran denies a planned dirty-bomb attack on Washington.", "flame"),
    ("MIDDLE EAST", "WEST BANK", "#b3402e", "A 72-year-old Palestinian woman is shot dead",
     "Settlers fired outside her home near Jericho, residents say.", "olive"),
    ("MIDDLE EAST", "ISRAEL", "#6d3fb5", "Knesset elects a speaker backed by Netanyahu\u2019s rivals",
     "Matan Kahana\u2019s win is a step to reversing the last government\u2019s laws.", "capitol"),
    ("EUROPE", "SANCTIONS", "#1a66c2", "Britain sanctions eight settlement builders",
     "Australia also sanctions Daniella Weiss, a \u201cgodmother\u201d of the settler project.", "gavel"),
    ("EUROPE", "MIGRATION", "#6d3fb5", "Five EU states plan \u201creturn hubs\u201d in Rwanda",
     "Germany, Austria, the Netherlands, Denmark and Greece sign up to the plan.", "gate"),
    ("EUROPE", "TRANSPORT", "#1a66c2", "Two trains collide in Prague, 46 hurt",
     "The crash came near the city\u2019s main railway station.", "train"),
    ("ASIA", "JAPAN", "#1a66c2", "Tokyo protests two Russian aircraft in its airspace",
     "They entered off the country\u2019s south-west, Japan says.", "plane"),
    ("ASIA", "PAKISTAN", "#0d8a4f", "Pakistan\u2019s solar boom outruns its grid",
     "Solar\u2019s share of electricity rose from 1% to 28% on rooftops.", "solar"),
    ("AFRICA", "GUINEA", "#0d8a4f", "Guinea jails 224 over illegal gold mining",
     "22 former officials and 202 miners were sentenced.", "pick"),
    ("AFRICA", "HEALTH", "#0d8a4f", "Ebola cases in DR Congo more than double",
     "The outbreak has doubled in three months, the UN says.", "virus"),
    ("AMERICAS", "TECH", "#c86a28", "Apple and Gmail go down days after Microsoft",
     "Another outage, and Americans ask who can fix this.", "outage"),
    ("AMERICAS", "ROADS", "#1a66c2", "California bans Waymo from its freeways",
     "The DMV calls the cars an \u201cimminent hazard\u201d after a closed-zone incident.", "car"),
]

BRIEFS = [
    ("Kyiv", 30.52, 50.45, "Ukraine", "Moscow strikes bridges in the capital, residents shelter underground"),
    ("Kerch", 36.47, 45.31, "Crimea", "the road bridge Russia built is cut by a missile and drone attack"),
    ("Moscow", 37.62, 55.75, "Russia", "Russian strikes hit bridges in Kyiv as the two sides trade blows"),
    ("Washington", -77.04, 38.90, "US", "Huang will testify to Congress on a \u201cnational security\u201d breach"),
    ("Washington", -77.04, 38.90, "US", "an appeals court blocks the Pentagon from expelling transgender troops"),
    ("Washington", -77.04, 38.90, "US", "the FAA halts router installation tied to Friday\u2019s ground stop"),
    ("Washington", -77.04, 38.90, "US", "a judge gives Trump until 22 January to sit for the BBC deposition"),
    ("Santa Clara", -121.96, 37.35, "US", "Nvidia doubles revenue and rules out reinstating its former chief"),
    ("Shenzhen", 114.06, 22.54, "China", "at APEC, Xi sends a \u201cChinamaxxing\u201d message from the host city"),
    ("Manila", 120.98, 14.60, "Philippines", "hundreds arrested in anti-Trump protests over Iran and AI"),
    ("Jericho", 35.44, 31.86, "Palestine", "a 72-year-old woman is shot dead outside her home"),
    ("Jerusalem", 35.21, 31.77, "Israel", "the Knesset elects Matan Kahana as its speaker"),
    ("Gaza", 34.46, 31.50, "Palestine", "winter rains flood makeshift shelters as aid is cut"),
    ("Manama", 50.58, 26.23, "Bahrain", "the human rights activist Nabeel Rajab dies at 62"),
    ("Tehran", 51.39, 35.69, "Iran", "Tehran denies reports of a planned dirty bomb in Washington"),
    ("Hormuz", 56.30, 26.60, "Strait", "an LPG tanker burns after a reported strike; the crew abandon ship"),
    ("Baghdad", 44.36, 33.31, "Iraq", "Kataib Hezbollah warns Iraqi forces off its stronghold"),
    ("Kabul", 69.18, 34.53, "Afghanistan", "women quietly defy the Taliban\u2019s bans on work and study"),
    ("Tokyo", 139.69, 35.69, "Japan", "Tokyo protests after two suspected Russian aircraft enter its airspace"),
    ("Seoul", 126.98, 37.57, "South Korea", "all aircraft will be grounded for 35 minutes on Thursday"),
    ("Brussels", 4.35, 50.85, "Belgium", "five states sign up to \u201creturn hubs\u201d in Rwanda for rejected migrants"),
    ("Berlin", 13.40, 52.52, "Germany", "one of the five; the plan is likely to face legal challenges"),
    ("Bratislava", 17.11, 48.15, "Slovakia", "crowds mark the Velvet Revolution by protesting Robert Fico"),
    ("Prague", 14.42, 50.08, "Czechia", "two trains collide near the main station, injuring 46"),
    ("Belgrade", 20.46, 44.79, "Serbia", "a military jet crashes north-west of the capital and the pilot dies"),
    ("Skopje", 21.43, 42.00, "N Macedonia", "four detained over an alleged Iran-backed plot in Greece"),
    ("Conakry", -13.68, 9.64, "Guinea", "224 people jailed over illegal gold mining in the north-east"),
    ("Kinshasa", 15.31, -4.32, "DR Congo", "Ebola cases more than double in three months"),
    ("Geneva", 6.14, 46.20, "Switzerland", "the UN rights office urges protection as abuses continue in Haiti"),
    ("Nairobi", 36.82, -1.29, "Kenya", "the WFP feeds families who fled violence in Ethiopia"),
    ("Port-au-Prince", -72.33, 18.54, "Haiti", "thousands rally for Bukele and the Salvadoran troops fighting gangs"),
    ("San Diego", -117.16, 32.72, "US", "an eight-year-old Haitian boy is released from ICE custody"),
    ("San Jos\u00e9", -84.09, 9.93, "Costa Rica", "a journalist is shot dead, the first such killing in 25 years"),
    ("Basseterre", -62.72, 17.30, "St Kitts", "the islands wind down their citizenship programme after EU threats"),
    ("Manaus", -60.02, -3.12, "Brazil", "an isolated Aw\u00e1 family makes contact, alarming researchers"),
    ("Bras\u00edlia", -47.93, -15.78, "Brazil", "1,605 pesticide poisoning reports, a third from EU-banned chemicals"),
    ("London", -0.13, 51.51, "UK", "Beckham sues Coty for $41m over cut-price fragrance sales"),
    ("London", -0.13, 51.51, "UK", "Equity wins actors rights over their digital replicas"),
]

PINS = None  # built from BRIEFS

ICONS = {
    "flame": '<path d="M13 3c4 6 6 8 6 12a6 6 0 0 1-12 0c0-4 2-6 6-12z" fill="#fff"/>',
    "olive": '<path d="M13 4c4 3 4 9 0 16-4-7-4-13 0-16z" fill="#fff"/><path d="M13 7v12" stroke="#b3402e" stroke-width="1.2"/>',
    "capitol": '<path d="M13 4l10 6H3z" fill="#fff"/><rect x="5" y="11" width="16" height="3" fill="#fff"/><path d="M7 15v6M12 15v6M17 15v6M4 22h18" stroke="#fff" stroke-width="2"/>',
    "gavel": '<rect x="14" y="4" width="9" height="5" rx="1" fill="#fff" transform="rotate(35 18 6)"/><path d="M4 22l10-10" stroke="#fff" stroke-width="2.4"/><path d="M11 20h12" stroke="#fff" stroke-width="2"/>',
    "gate": '<path d="M6 22V9a7 7 0 0 1 14 0v13" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M3 22h20" stroke="#fff" stroke-width="2"/>',
    "train": '<rect x="8" y="3" width="10" height="14" rx="3" fill="#fff"/><path d="M8 9h10M6 22l4-5M20 22l-4-5" stroke="#fff" stroke-width="2"/>',
    "plane": '<path d="M3 14l20-7-6 12-5-4-4 5-1-5z" fill="#fff"/>',
    "solar": '<rect x="4" y="7" width="18" height="11" rx="1" fill="#fff"/><path d="M4 12h18M13 7v11" stroke="#0d8a4f" stroke-width="1.2"/><path d="M13 21v2" stroke="#fff" stroke-width="2"/>',
    "pick": '<path d="M4 19q9-14 18-11" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M8 22l6-6" stroke="#fff" stroke-width="2.6"/>',
    "virus": '<circle cx="13" cy="13" r="6" fill="#fff"/><path d="M13 3v4M13 19v4M3 13h4M19 13h4M6 6l3 3M17 17l3 3M6 20l3-3M17 9l3-3" stroke="#fff" stroke-width="1.8"/>',
    "outage": '<path d="M4 12a12 12 0 0 1 18 0" fill="none" stroke="#fff" stroke-width="2.2"/><path d="M8 16a7 7 0 0 1 10 0" fill="none" stroke="#fff" stroke-width="2.2"/><circle cx="13" cy="20" r="2" fill="#fff"/><path d="M3 3l20 20" stroke="#fff" stroke-width="2"/>',
    "car": '<path d="M4 17l2-6h14l2 6v3H4z" fill="#fff"/><circle cx="8" cy="20" r="2" fill="#fff"/><circle cx="18" cy="20" r="2" fill="#fff"/>',
}

# --------------------------------------------------------------------- geometry
W = H = 1024
M = 42
CW = W - 2 * M
LEAD_W = (CW - 2 * 13) // 3
CARD_COLS = 4
CARD_W = (CW - 3 * 10) // 4
PAPER = "#f7f2e6"
INK = "#1b1712"
DIM = "#4a4234"
FAINT = "#6b6152"
RED = "#b3402e"

MAP_W, MAP_H = 282, 196
LON0, LON1 = -180.0, 180.0
LAT0, LAT1 = 78.0, -58.0

CONTINENTS = [
    [(-168, 66), (-156, 71), (-130, 70), (-110, 73), (-85, 70), (-62, 58), (-55, 47), (-66, 44),
     (-74, 38), (-76, 26), (-84, 30), (-81, 25), (-90, 29), (-97, 26), (-105, 20), (-110, 28),
     (-114, 33), (-124, 40), (-124, 48), (-135, 55), (-150, 60)],
    [(-45, 60), (-25, 70), (-22, 78), (-45, 80), (-60, 76), (-58, 66)],
    [(-78, 9), (-62, 11), (-50, 2), (-35, -6), (-38, -20), (-46, -28), (-54, -38), (-62, -52),
     (-70, -55), (-74, -44), (-72, -20), (-76, -6), (-80, 2)],
    [(-9, 38), (-9, 44), (-4, 48), (2, 51), (8, 54), (5, 58), (18, 60), (30, 61), (40, 56),
     (40, 46), (30, 41), (20, 40), (12, 38), (4, 43)],
    [(-17, 15), (-14, 22), (-8, 32), (2, 37), (11, 34), (25, 32), (34, 28), (43, 12), (51, 11),
     (45, -4), (40, -16), (32, -30), (25, -34), (16, -34), (10, -22), (2, -6), (-8, 4), (-15, 11)],
    [(30, 70), (45, 72), (70, 74), (95, 76), (125, 73), (160, 70), (178, 65), (170, 60), (155, 55),
     (143, 52), (135, 42), (129, 35), (122, 30), (108, 21), (100, 10), (98, 17), (88, 22), (80, 8),
     (72, 20), (68, 24), (58, 25), (50, 30), (43, 12), (35, 30), (32, 42)],
    [(68, 24), (74, 33), (88, 27), (80, 8), (72, 15)],
    [(129, 32), (133, 34), (137, 37), (141, 41), (145, 44), (142, 45), (140, 38), (136, 35), (131, 33)],
    [(95, 6), (106, -6), (115, -8), (125, -9), (135, -4), (140, -8), (130, -9), (120, -9), (110, -7), (100, 0)],
    [(119, 6), (123, 18), (126, 6), (121, 2)],
    [(113, -21), (114, -33), (124, -35), (138, -35), (150, -37), (153, -28), (145, -15), (130, -12), (119, -20)],
    [(172, -34), (178, -38), (174, -41), (167, -46), (170, -38)],
]


def project(lon, lat, ox, oy, w=MAP_W, h=MAP_H):
    """Equirectangular: longitude and latitude to a point on the plate."""
    x = ox + (lon - LON0) / (LON1 - LON0) * w
    y = oy + (LAT0 - lat) / (LAT0 - LAT1) * h
    return x, y


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_node(x, y, text, size, weight=400, fill=INK, anchor="start", serif=True, spacing=None):
    family = "Georgia, serif" if serif else "Arial, Helvetica, sans-serif"
    track = ' letter-spacing="%s"' % spacing if spacing else ""
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s"'
            ' text-anchor="%s"%s>%s</text>') % (x, y, family, size, weight, fill, anchor, track, esc(text))


def sans_width(text_value, size):
    return width(text_value, ARIAL, size)


# --------------------------------------------------------------------- the leads' scenes
def scene_bridge(ox, oy, w):
    """A span coming down: the bridge, one tower left standing, the water below."""
    out = ['<rect x="%d" y="%d" width="%d" height="128" fill="#1b2233"/>' % (ox, oy, w)]
    for k in range(40):
        sx = ox + 4 + (k * 37) % (w - 8)
        sy = oy + 12 + (k * 23) % 44
        out.append('<circle cx="%d" cy="%d" r="0.8" fill="#8f9dc0" opacity="0.7"/>' % (sx, sy))
    out.append('<circle cx="%d" cy="%d" r="11" fill="#f6e7c4"/>' % (ox + w - 34, oy + 26))
    out.append('<rect x="%d" y="%d" width="%d" height="52" fill="#101828"/>' % (ox, oy + 60, w))
    out.append('<path d="M%d %d q%f -4 14 0" stroke="#2b3a55" stroke-width="1.4" fill="none"/>'
               % (ox + 20, oy + 70, w * 0.3))
    # the standing towers
    for tx in (ox + 26, ox + w - 46):
        out.append('<path d="M%d %d l6 -26 l6 26" fill="none" stroke="#5b6c8f" stroke-width="2.4"/>' % (tx, oy + 60))
        out.append('<path d="M%d %d h12" stroke="#5b6c8f" stroke-width="1.6"/>' % (tx, oy + 38))
    # the deck, broken in the middle
    out.append('<rect x="%d" y="%d" width="%d" height="5" fill="#7d8db0"/>' % (ox + 4, oy + 58, int(w * 0.38)))
    out.append('<rect x="%d" y="%d" width="%d" height="5" fill="#7d8db0"/>' % (ox + int(w * 0.66), oy + 56, int(w * 0.3)))
    out.append('<path d="M%d %d l26 34 l12 -2" fill="none" stroke="#94a2c2" stroke-width="4"/>'
               % (ox + int(w * 0.4), oy + 60))
    out.append('<path d="M%d %d l18 30" fill="none" stroke="#94a2c2" stroke-width="4"/>' % (ox + int(w * 0.62), oy + 58))
    # the strike: two trails and a burst
    for sx, sy, ex, ey in ((ox + 18, oy + 34, ox + int(w * 0.44), oy + 56), (ox + 40, oy + 20, ox + int(w * 0.56), oy + 54)):
        out.append('<path d="M%d %d Q%d %d %d %d" fill="none" stroke="#e0603a" stroke-width="1.8" stroke-dasharray="5 4"/>'
                   % (sx, sy, (sx + ex) // 2, sy - 10, ex, ey))
    out.append('<circle cx="%d" cy="%d" r="9" fill="#ffb07a" opacity="0.9"/>' % (ox + int(w * 0.5), oy + 56))
    out.append('<circle cx="%d" cy="%d" r="16" fill="#ff8a4a" opacity="0.25"/>' % (ox + int(w * 0.5), oy + 56))
    # the water
    for k in range(4):
        out.append('<path d="M%d %d q12 -3 24 0 t24 0" stroke="#2f4468" stroke-width="1.2" fill="none"/>'
                   % (ox + 8 + k * 10, oy + 74 + k * 7))
    out.append('<rect x="%d" y="%d" width="%d" height="15" fill="#1a66c2"/>' % (ox, oy, w))
    out.append(text_node(ox + 8, oy + 11, "KERCH \u00b7 THE SPAN IS DOWN", 9.5, 700, "#ffffff", serif=False, spacing="1.1"))
    out.append('<rect x="%d" y="%d" width="%d" height="16" fill="#1a66c2"/>' % (ox, oy + 112, w))
    out.append(text_node(ox + 8, oy + 124, "MOSCOW HITS KYIV\u2019S BRIDGES IN RETURN", 8.4, 700, "#dbe7fb", serif=False, spacing="0.9"))
    return out


def scene_chip(ox, oy, w):
    """A die under a lens: the quarter that doubled, and a hearing waiting."""
    out = ['<rect x="%d" y="%d" width="%d" height="128" fill="#241f2e"/>' % (ox, oy, w)]
    out.append('<circle cx="%d" cy="%d" r="34" fill="#3a3350"/>' % (ox + w // 2, oy + 64))
    out.append('<rect x="%d" y="%d" width="52" height="52" rx="6" fill="#0f1420" stroke="#7a6fa8" stroke-width="2"/>'
               % (ox + w // 2 - 26, oy + 38))
    for r in range(3):
        for c in range(3):
            out.append('<rect x="%d" y="%d" width="6" height="6" rx="1" fill="#c9a227"/>'
                       % (ox + w // 2 - 20 + c * 17, oy + 44 + r * 16))
    out.append('<path d="M%d %d l-14 6 M%d %d l14 6 M%d %d l-14 -6 M%d %d l14 -6" stroke="#7a6fa8" stroke-width="2"/>'
               % (ox + w // 2 - 26, oy + 50, ox + w // 2 + 26, oy + 50, ox + w // 2 - 26, oy + 78, ox + w // 2 + 26, oy + 78))
    # a rising line: revenue doubled
    pts = []
    for k in range(9):
        px = ox + 12 + k * (w - 24) / 8
        py = oy + 104 - math.pow(1.35, k) * 2.2
        pts.append("%.1f,%.1f" % (px, max(oy + 34, py)))
    out.append('<polyline points="%s" fill="none" stroke="#4cc9f0" stroke-width="2.2"/>' % " ".join(pts))
    for k, p in enumerate(pts):
        if k % 2 == 0:
            x, y = p.split(",")
            out.append('<circle cx="%s" cy="%s" r="2.2" fill="#ffd166"/>' % (x, y))
    out.append('<rect x="%d" y="%d" width="%d" height="15" fill="#c86a28"/>' % (ox, oy, w))
    out.append(text_node(ox + 8, oy + 11, "SANTA CLARA \u00b7 NO HUANG", 9.5, 700, "#ffffff", serif=False, spacing="1.1"))
    out.append('<rect x="%d" y="%d" width="%d" height="16" fill="#c86a28"/>' % (ox, oy + 112, w))
    out.append(text_node(ox + 8, oy + 124, "AND A CONGRESSIONAL HEARING AHEAD", 8.4, 700, "#ffe9c9", serif=False, spacing="0.9"))
    return out


def scene_measles(ox, oy, w):
    """A chart of the outbreak and a falling shield: the status lost."""
    out = ['<rect x="%d" y="%d" width="%d" height="128" fill="#f6ece3"/>' % (ox, oy, w)]
    out.append('<rect x="%d" y="%d" width="%d" height="128" fill="#b3402e" opacity="0.08"/>' % (ox, oy, w))
    # bars: the year's cases
    for k, h in enumerate((10, 14, 18, 26, 40, 52, 66, 74)):
        bx = ox + 14 + k * 17
        out.append('<rect x="%d" y="%d" width="12" height="%d" fill="%s" rx="2"/>'
                   % (bx, oy + 100 - h, h, "#b3402e" if k < 6 else "#8d2f21"))
    out.append('<path d="M%d %d h%d" stroke="#b3402e" stroke-width="1.4"/>' % (ox + 12, oy + 101, 148))
    for k in range(4):
        out.append(text_node(ox + 12, oy + 111 + k * 0, "", 8, 400, DIM, serif=False))
    # the shield with a crack
    cx, cy = ox + w - 66, oy + 62
    out.append('<path d="M%d %d l30 -12 l30 12 v26 q0 30 -30 42 q-30 -12 -30 -42 z" fill="#ffffff" stroke="#b3402e" stroke-width="2"/>'
               % (cx, cy))
    out.append('<path d="M%d %d l10 14 l-8 10 l12 12" fill="none" stroke="#b3402e" stroke-width="2.2"/>' % (cx + 30, cy + 6))
    out.append(text_node(ox + 12, oy + 30, "CASES, 2026", 8.6, 700, "#8d2f21", serif=False, spacing="1.2"))
    out.append('<rect x="%d" y="%d" width="%d" height="15" fill="#b3402e"/>' % (ox, oy, w))
    out.append(text_node(ox + 8, oy + 11, "WASHINGTON \u00b7 26 YEARS GONE", 9.5, 700, "#ffffff", serif=False, spacing="1.1"))
    out.append('<rect x="%d" y="%d" width="%d" height="16" fill="#b3402e"/>' % (ox, oy + 112, w))
    out.append(text_node(ox + 8, oy + 124, "5,400 CASES \u00b7 10 DEATHS THIS YEAR", 8.4, 700, "#f7d9cd", serif=False, spacing="0.9"))
    return out


SCENES = {"bridge": scene_bridge, "chip": scene_chip, "measles": scene_measles}


# --------------------------------------------------------------------- the page
def page():
    out = []
    add = out.append
    add('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">')
    add('<rect width="1024" height="1024" fill="%s"/>' % PAPER)
    add('<rect x="0" y="0" width="1024" height="9" fill="%s"/>' % INK)

    stories = len(LEADS) + len(CARDS) + len(BRIEFS)
    countries = len(set(b[3] for b in BRIEFS))
    add(text_node(M, 44, "THE DAY", 14, 700, RED, serif=False, spacing="2.6"))
    add(text_node(W - M, 44, "%d STORIES \u00b7 %d COUNTRIES \u00b7 ALL FROM TUESDAY" % (stories, countries),
                  12.5, 700, FAINT, "end", serif=False, spacing="1.5"))
    add(text_node(W / 2, 112, "Tuesday 17 November 2026", 58, 700, INK, "middle"))
    add('<line x1="%d" y1="132" x2="%d" y2="132" stroke="%s" stroke-width="3"/>' % (M, W - M, INK))
    add('<line x1="%d" y1="138" x2="%d" y2="138" stroke="%s" stroke-width="1"/>' % (M, W - M, INK))

    # the three leads
    top = 152
    for i, lead in enumerate(LEADS):
        x = M + i * (LEAD_W + 13)
        add('<rect x="%d" y="%d" width="%d" height="274" fill="#fdfbf4" stroke="#e2dac6"/>' % (x, top, LEAD_W))
        for node in SCENES[lead["scene"]](x + 10, top + 10, LEAD_W - 20):
            add(node)
        y = top + 156
        add('<circle cx="%d" cy="%d" r="6.5" fill="%s"/>' % (x + 16, y - 4, lead["colour"]))
        add(text_node(x + 27, y, lead["region"], 10.5, 700, lead["colour"], serif=False, spacing="1.2"))
        lines = wrap(lead["title"], LEAD_W - 24, GEORGIA_B, 18)[:3]
        for j, line in enumerate(lines):
            add(text_node(x + 12, y + 24 + j * 22, line, 18, 700))
        body = y + 24 + 22 * len(lines) + 2
        for j, line in enumerate(wrap(lead["blurb"], LEAD_W - 24, ARIAL, 11.5)[:4]):
            add(text_node(x + 12, body + j * 14.5, line, 11.5, 400, DIM, serif=False))

    # the numbers
    ny = top + 296
    add('<rect x="%d" y="%d" width="%d" height="48" fill="#efe8d6"/>' % (M, ny, CW))
    col = CW // len(NUMBERS)
    for i, (figure, label) in enumerate(NUMBERS):
        nx = M + i * col
        if i:
            add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#d8cfb6"/>' % (nx, ny + 8, nx, ny + 40))
        add(text_node(nx + 14, ny + 23, figure, 18.5, 700, RED, serif=False))
        for j, line in enumerate(label.split("\n")):
            add(text_node(nx + 14, ny + 35 + j * 10, line, 9.2, 400, DIM, serif=False))

    # the cards
    cy = ny + 64
    card_h = 76
    for i, (region, topic, colour, title, blurb, icon) in enumerate(CARDS):
        row, column = divmod(i, CARD_COLS)
        x = M + column * (CARD_W + 10)
        y = cy + row * (card_h + 8)
        add('<rect x="%d" y="%d" width="%d" height="%d" fill="#fdfbf4" stroke="#e2dac6"/>' % (x, y, CARD_W, card_h))
        add('<rect x="%d" y="%d" width="3" height="%d" fill="%s"/>' % (x, y, card_h, colour))
        add('<rect x="%d" y="%d" width="22" height="22" rx="6" fill="%s"/>' % (x + 10, y + 10, colour))
        add('<g transform="translate(%d %d)">%s</g>' % (x + 10, y + 10, ICONS[icon]))
        add(text_node(x + 38, y + 17, region + " \u00b7 " + topic, 8.4, 700, colour, serif=False, spacing="0.8"))
        for j, line in enumerate(wrap(title, CARD_W - 48, ARIAL_B, 11.3)[:2]):
            add(text_node(x + 38, y + 29 + j * 12.4, line, 11.3, 700, INK, serif=False))
        for j, line in enumerate(wrap(blurb, CARD_W - 20, ARIAL, 9.3)[:2]):
            add(text_node(x + 10, y + 54 + j * 10.8, line, 9.3, 400, DIM, serif=False))

    # the map and the briefs
    my = cy + 3 * (card_h + 8) + 6
    mh = H - my - 50
    add('<rect x="%d" y="%d" width="%d" height="%d" fill="#e4eddf"/>' % (M, my, MAP_W, mh))
    add('<rect x="%d" y="%d" width="%d" height="19" fill="%s"/>' % (M, my, MAP_W, INK))
    add('<text x="%d" y="%d" font-family="Arial" font-size="8.2" font-weight="700" fill="%s" letter-spacing="1.2">WHERE IT HAPPENED</text>'
        % (M + 9, my + 13, PAPER))
    add('<text x="%d" y="%d" font-family="Arial" font-size="7.2" font-weight="700" fill="#bdb3a0" text-anchor="end">%d PLACES</text>'
        % (M + MAP_W - 8, my + 13, len(BRIEFS)))
    for poly in CONTINENTS:
        points = " ".join("%.1f,%.1f" % project(lon, lat, M, my + 19, MAP_W, mh - 19) for lon, lat in poly)
        add('<polygon points="%s" fill="#cfc0a2" stroke="#b9a888" stroke-width="0.7"/>' % points)

    spots = []
    for city, lon, lat, country, brief in BRIEFS:
        px, py = project(lon, lat, M, my + 19, MAP_W, mh - 19)
        spots.append([px, py, px, py])
    # crowded pins are pulled apart, each tied to its own place by a leader line
    for _ in range(60):
        moved = False
        for a in range(len(spots)):
            for b in range(a + 1, len(spots)):
                dx = spots[b][2] - spots[a][2]
                dy = spots[b][3] - spots[a][3]
                dist = math.hypot(dx, dy)
                if dist < 15.0:
                    if dist < 0.01:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (15.0 - dist) / 2.0 + 0.4
                    spots[a][2] -= dx / dist * push
                    spots[a][3] -= dy / dist * push
                    spots[b][2] += dx / dist * push
                    spots[b][3] += dy / dist * push
                    moved = True
        for spot in spots:
            spot[2] = min(max(spot[2], M + 9), M + MAP_W - 10)
            spot[3] = min(max(spot[3], my + 26), my + mh - 8)
        if not moved:
            break
    for i, (px, py, dx, dy) in enumerate(spots):
        if abs(dx - px) > 0.4 or abs(dy - py) > 0.4:
            add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8"/>' % (px, py, dx, dy, DIM))
            add('<circle cx="%.1f" cy="%.1f" r="1.3" fill="%s"/>' % (px, py, DIM))
        add('<circle cx="%.1f" cy="%.1f" r="6.6" fill="%s"/>' % (dx, dy, INK))
        add('<circle cx="%.1f" cy="%.1f" r="6.6" fill="none" stroke="%s" stroke-width="1.1"/>' % (dx, dy, PAPER))
        add('<text x="%.1f" y="%.1f" font-family="Arial" font-size="7.8" font-weight="700" fill="%s" text-anchor="middle">%d</text>'
            % (dx, dy + 2.7, PAPER, i + 1))

    ox = M + MAP_W + 14
    ow = W - M - ox
    add(text_node(ox, my + 12, "ALSO ON TUESDAY 17 NOVEMBER", 10, 700, RED, serif=False, spacing="1.1"))
    columns = 2
    colw = ow // columns
    per = (len(BRIEFS) + columns - 1) // columns
    rowh = (mh - 30) / per
    for i, (city, lon, lat, country, brief) in enumerate(BRIEFS):
        column, row = divmod(i, per)
        x = ox + column * colw
        y = my + 24 + row * rowh
        add(text_node(x, y, "%d" % (i + 1), 8, 700, RED, "end", serif=False))
        add(text_node(x + 12, y, city + ":", 9.2, 700, INK, serif=False))
        start = x + 14 + sans_width(city + ":", 9.2)
        room = (colw - (start - x) - 10) * 0.93
        add(text_node(start, y, clip(brief, room, ARIAL, 9.2), 9.2, 400, DIM, serif=False))

    # the footer
    fy = H - 44
    add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#cdc2a9"/>' % (M, fy, W - M, fy))
    add(text_node(M, fy + 13, "SOURCES: BBC, THE GUARDIAN, AL JAZEERA, UN NEWS, NPR, ABC, CBC, SKY, CNBC \u00b7 17 NOVEMBER 2026",
                  10, 400, FAINT, serif=False, spacing="0.6"))
    add(text_node(M, fy + 26, "EVERY STORY HAPPENED OR WAS FIRST REPORTED THAT DAY \u00b7 CONTESTED CLAIMS ARE MARKED AS CLAIMS \u00b7 %d PLOTTED PLACES" % len(BRIEFS),
                  10, 700, FAINT, serif=False, spacing="0.6"))
    add('</svg>')
    return "\n".join(out)


def main():
    drawing = page()
    html = ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
            '@page{size:1024px 1024px;margin:0}'
            'html,body{margin:0;padding:0;width:1024px;height:1024px;overflow:hidden;background:%s}'
            '</style></head><body>%s</body></html>') % (PAPER, drawing)
    io.open("plate.html", "w", encoding="utf-8").write(html)
    print("wrote plate.html (%d bytes)" % len(html))


if __name__ == "__main__":
    main()
