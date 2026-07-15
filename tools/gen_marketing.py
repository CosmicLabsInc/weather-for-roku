#!/usr/bin/env python3
"""Generate Roku channel-store marketing art: a promo poster and screenshots.

Screenshots are pixel-accurate mockups composited from the app's real assets
(background, cards, weather icons, keypad chrome) so they match the on-device UI.
Rendered at the app's native 1280x720 and upscaled to 1920x1080 for the store.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "marketing")
os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

# colors from the UI (RGB)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
DIM = (100, 116, 139)
CYAN = (125, 211, 252)
FAINT = (71, 85, 105)
LINE = (51, 65, 85)


def font(bold, size):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    except Exception:
        return ImageFont.load_default()


def load(rel):
    return Image.open(os.path.join(IMG, rel)).convert("RGBA")


def ctext(d, cx, y, text, f, fill):
    """Draw horizontally centered around cx, top at y."""
    b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], y), text, font=f, fill=fill)


# system-font pixel approximations at 720p
F_LARGE = font(True, 42)
F_MEDB = font(True, 27)
F_MED = font(False, 26)
F_SMALL = font(False, 21)

ICON = {
    "Sunny": "clear.png",
    "Partly Cloudy": "partly_cloudy.png",
    "Showers": "showers.png",
    "Storms": "thunderstorm.png",
    "Rain": "rain.png",
    "Cloudy": "cloudy.png",
    "Snow": "snow.png",
}

SAMPLE_DAYS = [
    ("Today", "Sunny", 88, 64, 0, True),
    ("Mon", "Partly Cloudy", 85, 62, 10, False),
    ("Tue", "Showers", 79, 60, 60, False),
    ("Wed", "Storms", 74, 58, 80, False),
    ("Thu", "Rain", 71, 57, 70, False),
    ("Fri", "Partly Cloudy", 80, 61, 20, False),
    ("Sat", "Sunny", 86, 63, 0, False),
]

# Today's hourly strip: (time, condition, temp, is_now)
SAMPLE_HOURS = [
    ("Now", "Sunny", 88, True),
    ("3PM", "Sunny", 89, False),
    ("4PM", "Sunny", 88, False),
    ("5PM", "Partly Cloudy", 86, False),
    ("6PM", "Partly Cloudy", 84, False),
    ("7PM", "Cloudy", 82, False),
    ("8PM", "Cloudy", 80, False),
]

CARD_Y = 112


def draw_card(base, x, day, cond, hi, lo, precip, today):
    card = load("ui/card_today.png" if today else "ui/card.png")
    base.alpha_composite(card, (x, CARD_Y))
    d = ImageDraw.Draw(base)
    cx = x + 75
    ctext(d, cx, CARD_Y + 24, day, F_MEDB, CYAN if today else WHITE)
    icon = load("weather/" + ICON.get(cond, "cloudy.png")).resize((80, 80), Image.LANCZOS)
    base.alpha_composite(icon, (x + 35, CARD_Y + 70))
    ctext(d, cx, CARD_Y + 166, cond, F_SMALL, MUTED)
    ctext(d, cx, CARD_Y + 220, f"{hi}\u00b0", F_LARGE, WHITE)
    ctext(d, cx, CARD_Y + 280, f"{lo}\u00b0", F_MED, DIM)
    ctext(d, cx, CARD_Y + 326, f"{precip}% rain", F_SMALL, CYAN)


def draw_hourly(base):
    """Today's always-on hourly strip beneath the 7-day row, in the Today-tile
    color with a tab under the Today card so it reads as expanding out of it."""
    d = ImageDraw.Draw(base)
    panel = load("ui/hourly.png")  # 1098x130 with top tab
    px, py = 91, 494
    base.alpha_composite(panel, (px, py))

    row_y = 508  # body top (below the 14px tab)
    hi_cond = (203, 213, 225)  # light slate, readable on the blue panel
    f_time = font(True, 21)
    # Cell centers evenly span the day-card centers: Today=166 .. Sat=1114.
    left_c, right_c = px + 75, px + 1023
    n = len(SAMPLE_HOURS)
    pitch = (right_c - left_c) / (n - 1)
    for i, (label, cond, temp, is_now) in enumerate(SAMPLE_HOURS):
        cx = round(left_c + i * pitch)
        ctext(d, cx, row_y + 7, label, f_time, CYAN if is_now else WHITE)
        icon = load("weather/" + ICON.get(cond, "cloudy.png")).resize((36, 36), Image.LANCZOS)
        base.alpha_composite(icon, (cx - 18, row_y + 27))
        ctext(d, cx, row_y + 62, f"{temp}\u00b0", F_MEDB, WHITE)
        ctext(d, cx, row_y + 90, cond, F_SMALL, hi_cond)


def screenshot_forecast():
    base = load("bg_gradient.png").resize((1280, 720), Image.LANCZOS)
    d = ImageDraw.Draw(base)
    ctext(d, 640, 32, "Aurora, IL", F_LARGE, WHITE)
    ctext(d, 640, 78, "ZIP 60504   \u2022   7-Day Forecast", F_SMALL, CYAN)

    n = len(SAMPLE_DAYS)
    cw, gap = 150, 8
    total = n * cw + (n - 1) * gap
    startx = (1280 - total) // 2
    for i, (day, cond, hi, lo, pr, today) in enumerate(SAMPLE_DAYS):
        draw_card(base, startx + i * (cw + gap), day, cond, hi, lo, pr, today)

    draw_hourly(base)

    ctext(d, 640, 650, "Press * to change ZIP code", F_SMALL, FAINT)
    return base


def screenshot_zip():
    base = load("bg_gradient.png").resize((1280, 720), Image.LANCZOS)
    base.alpha_composite(load("ui/panel.png").resize((640, 600)), (320, 60))
    base.alpha_composite(load("brand_icon.png").resize((96, 96)), (592, 82))
    d = ImageDraw.Draw(base)
    ctext(d, 640, 188, "Weather", F_LARGE, WHITE)
    ctext(d, 640, 236, "Enter your US ZIP code", F_MED, MUTED)

    # digit boxes (462,284); show "60504" filled
    zip_str = "60504"
    xs = [0, 74, 148, 222, 296]
    for i, dx in enumerate(xs):
        base.alpha_composite(load("ui/digit_filled.png").resize((60, 74)), (462 + dx, 284))
        ctext(d, 462 + dx + 30, 284 + 16, zip_str[i], font(True, 40), WHITE)

    # numpad (482,376): 3 cols x 4 rows, keyW96 keyH54 gapX14 gapY8
    labels = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["DEL", "0", "GO"]]
    key = load("ui/key.png").resize((96, 54))
    keyact = load("ui/key_action.png").resize((96, 54))
    focus = load("ui/key_focus.png").resize((116, 74))
    for r in range(4):
        for c in range(3):
            gx, gy = 482 + c * 110, 376 + r * 62
            base.alpha_composite(keyact if labels[r][c] == "GO" else key, (gx, gy))
    # focus highlight on "5" (row1,col1)
    base.alpha_composite(focus, (482 + 1 * 110 - 10, 376 + 1 * 62 - 10))
    for r in range(4):
        for c in range(3):
            gx, gy = 482 + c * 110, 376 + r * 62
            lab = labels[r][c]
            fnt = font(True, 22) if lab in ("GO", "DEL") else font(True, 30)
            b = d.textbbox((0, 0), lab, font=fnt)
            d.text((gx + 48 - (b[2] - b[0]) / 2 - b[0], gy + 27 - (b[3] - b[1]) / 2 - b[1]),
                   lab, font=fnt, fill=WHITE)

    ctext(d, 640, 626, "Use the arrows and OK. Select GO when done.", F_SMALL, DIM)
    return base


def poster():
    W, H = 1920, 1080
    from PIL import ImageFilter
    # navy vertical gradient
    top, bot = (10, 20, 36), (22, 42, 70)
    base = Image.new("RGB", (W, H))
    for y in range(H):
        t = y / (H - 1)
        base.putpixel((0, y), 0)  # placeholder
    px = base.load()
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = col
    base = base.convert("RGBA")

    # cyan glow accent top-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gr = 620
    gd.ellipse([W - gr, -gr // 2, W + gr // 2, gr], fill=(56, 189, 248, 34))
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    base = Image.alpha_composite(base, glow)

    d = ImageDraw.Draw(base)
    # brand icon
    icon = load("brand_icon.png").resize((150, 150), Image.LANCZOS)
    base.alpha_composite(icon, (W // 2 - 75, 120))
    ctext(d, W // 2, 300, "Weather", font(True, 108), WHITE)
    ctext(d, W // 2, 430, "Your local 7-day forecast, beautifully simple.",
          font(False, 40), MUTED)
    # cyan underline
    d.rounded_rectangle([W // 2 - 90, 415, W // 2 + 90, 421], radius=3, fill=CYAN)

    # a floating row of all 7 sample cards near bottom
    demo = SAMPLE_DAYS
    scale = 1.0
    cw = int(150 * scale)
    ch = int(412 * scale)
    gap = 24
    total = len(demo) * cw + (len(demo) - 1) * gap
    startx = (W - total) // 2
    cy = 560
    for i, (day, cond, hi, lo, pr, today) in enumerate(demo):
        x = startx + i * (cw + gap)
        card = load("ui/card_today.png" if today else "ui/card.png").resize((cw, ch), Image.LANCZOS)
        base.alpha_composite(card, (x, cy))
        cx = x + cw // 2
        ctext(d, cx, cy + int(26 * scale), day, font(True, int(27)), CYAN if today else WHITE)
        ic = load("weather/" + ICON.get(cond, "cloudy.png")).resize((int(80 * scale), int(80 * scale)), Image.LANCZOS)
        base.alpha_composite(ic, (x + int(35 * scale), cy + int(74 * scale)))
        ctext(d, cx, cy + int(176 * scale), cond, font(False, 20), MUTED)
        ctext(d, cx, cy + int(240 * scale), f"{hi}\u00b0", font(True, 40), WHITE)
        ctext(d, cx, cy + int(300 * scale), f"{lo}\u00b0", font(False, 25), DIM)
        ctext(d, cx, cy + int(358 * scale), f"{pr}% rain", font(False, 20), CYAN)

    return base.convert("RGB")


def screenshot_loading():
    base = load("bg_gradient.png").resize((1280, 720), Image.LANCZOS)
    spin = load("ui/spinner.png").resize((100, 100), Image.LANCZOS)
    base.alpha_composite(spin, (640 - 50, 300 - 50))
    d = ImageDraw.Draw(base)
    ctext(d, 640, 400, "Fetching your forecast\u2026", F_MED, MUTED)
    return base


def app_poster():
    """540x405 (4:3) Streaming Store poster."""
    from PIL import ImageFilter
    W, H = 540, 405
    SS = 3
    cw, ch = W * SS, H * SS
    top, bot = (10, 20, 36), (22, 42, 70)
    base = Image.new("RGB", (cw, ch))
    px = base.load()
    for y in range(ch):
        t = y / (ch - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(cw):
            px[x, y] = col
    base = base.convert("RGBA")

    glow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gr = int(ch * 0.8)
    gd.ellipse([cw - gr, -gr // 2, cw + gr // 2, gr], fill=(56, 189, 248, 34))
    glow = glow.filter(ImageFilter.GaussianBlur(ch * 0.10))
    base = Image.alpha_composite(base, glow)

    icon = load("brand_icon.png").resize((120 * SS, 120 * SS), Image.LANCZOS)
    base.alpha_composite(icon, (cw // 2 - 60 * SS, 44 * SS))
    d = ImageDraw.Draw(base)
    ctext(d, cw // 2, 184 * SS, "Weather", font(True, 66 * SS), WHITE)
    d.rounded_rectangle([cw // 2 - 52 * SS, 250 * SS, cw // 2 + 52 * SS, 255 * SS],
                        radius=3 * SS, fill=CYAN)
    ctext(d, cw // 2, 272 * SS, "Simple 7-day forecast", font(False, 26 * SS), MUTED)

    # small decorative weather glyphs row
    glyphs = ["clear.png", "partly_cloudy.png", "rain.png"]
    gsz = 62 * SS
    total = len(glyphs) * gsz + (len(glyphs) - 1) * 30 * SS
    sx = (cw - total) // 2
    for i, g in enumerate(glyphs):
        ic = load("weather/" + g).resize((gsz, gsz), Image.LANCZOS)
        base.alpha_composite(ic, (sx + i * (gsz + 30 * SS), 318 * SS))

    return base.resize((W, H), Image.LANCZOS).convert("RGB")


def save_shot(img720, name):
    img720.convert("RGB").save(os.path.join(OUT, name + "_720.png"))
    img720.resize((1920, 1080), Image.LANCZOS).convert("RGB").save(
        os.path.join(OUT, name + ".png"))


if __name__ == "__main__":
    save_shot(screenshot_forecast(), "screenshot_forecast")
    save_shot(screenshot_zip(), "screenshot_zip")
    save_shot(screenshot_loading(), "screenshot_loading")
    app_poster().save(os.path.join(OUT, "app_poster_540x405.png"))
    poster().save(os.path.join(OUT, "promo_16x9.png"))
    print("marketing art done ->", OUT)
