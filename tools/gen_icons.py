#!/usr/bin/env python3
"""Modern, minimalist weather icon set + app art for the Roku Weather channel.

Rendered at 4x supersampling with soft gradients, teardrop rain, gentle
cloud shadows, and a radial sun for a clean, pleasant, contemporary look.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "images")
WX = os.path.join(IMG, "weather")
UI = os.path.join(IMG, "ui")
for p in (WX, UI):
    os.makedirs(p, exist_ok=True)

SS = 4

# ---- palette -------------------------------------------------------------
SUN_CORE = (255, 214, 102)
SUN_EDGE = (255, 176, 59)
SUN_RAY = (255, 200, 74)
CLOUD_TOP = (255, 255, 255)
CLOUD_BOT = (223, 233, 245)
GRAY_TOP = (179, 190, 206)
GRAY_BOT = (135, 149, 170)
RAIN_TOP = (99, 197, 247)
RAIN_BOT = (43, 155, 230)
SNOW = (238, 246, 253)
FOG = (200, 212, 228)
BOLT = (255, 199, 61)


def lerp(a, b, t):
    return int(round(a + (b - a) * t))


def lerp3(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))


def vgrad(w, h, top, bottom, ease=False):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        if ease:
            t = t * t * (3 - 2 * t)
        c = lerp3(top, bottom, t)
        for x in range(w):
            px[x, y] = c
    return img.convert("RGBA")


# ---- primitives ----------------------------------------------------------

def _cloud_shape(draw, cx, cy, w, fill):
    h = w * 0.66
    draw.rounded_rectangle(
        [cx - w * 0.5, cy - h * 0.02, cx + w * 0.5, cy + h * 0.44],
        radius=h * 0.44, fill=fill)
    draw.ellipse([cx - w * 0.5, cy - h * 0.22, cx - w * 0.04, cy + h * 0.36], fill=fill)
    draw.ellipse([cx + w * 0.02, cy - h * 0.16, cx + w * 0.5, cy + h * 0.38], fill=fill)
    draw.ellipse([cx - w * 0.28, cy - h * 0.56, cx + w * 0.30, cy + h * 0.14], fill=fill)


def put_cloud(img, cx, cy, w, top=CLOUD_TOP, bot=CLOUD_BOT, shadow=True):
    W, H = img.size
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        _cloud_shape(sd, cx, cy + w * 0.11, w, (8, 22, 45, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(w * 0.055))
        img.alpha_composite(sh)
    mask = Image.new("L", (W, H), 0)
    _cloud_shape(ImageDraw.Draw(mask), cx, cy, w, 255)
    grad = vgrad(W, H, top, bot)
    grad.putalpha(mask)
    img.alpha_composite(grad)


def put_sun(img, cx, cy, r, rays=True):
    W, H = img.size
    if rays:
        d = ImageDraw.Draw(img)
        n = 12
        inner, outer = r * 1.30, r * 1.74
        wdt = max(2, int(r * 0.16))
        for i in range(n):
            a = (2 * math.pi / n) * i + math.pi / n
            x1, y1 = cx + math.cos(a) * inner, cy + math.sin(a) * inner
            x2, y2 = cx + math.cos(a) * outer, cy + math.sin(a) * outer
            d.line([(x1, y1), (x2, y2)], fill=SUN_RAY, width=wdt)
            cap = wdt * 0.5
            d.ellipse([x2 - cap, y2 - cap, x2 + cap, y2 + cap], fill=SUN_RAY)
    # radial disc: draw from edge inward
    disc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    steps = int(r)
    for i in range(steps, 0, -1):
        t = i / steps
        col = lerp3(SUN_CORE, SUN_EDGE, t)
        dd.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(col[0], col[1], col[2], 255))
    img.alpha_composite(disc)


def teardrop(dw, dh, top, bot):
    im = Image.new("RGBA", (int(dw), int(dh)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = dw / 2
    mask = Image.new("L", (int(dw), int(dh)), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, dh - 2 * r, dw, dh], fill=255)
    md.polygon([(dw / 2, 0), (1, dh - r), (dw - 1, dh - r)], fill=255)
    grad = vgrad(int(dw), int(dh), top, bot)
    grad.putalpha(mask)
    im.alpha_composite(grad)
    # soft highlight
    d.ellipse([dw * 0.30, dh - 1.7 * r, dw * 0.52, dh - 1.15 * r], fill=(255, 255, 255, 90))
    return im


def put_rain(img, cx, top_y, spread, n, dw, dh, top=RAIN_TOP, bot=RAIN_BOT):
    drop = teardrop(dw, dh, top, bot)
    for i in range(n):
        x = cx - spread / 2 + (spread / (n - 1)) * i if n > 1 else cx
        y = top_y + (dh * 0.18 if i % 2 else 0)
        img.alpha_composite(drop, (int(x - dw / 2), int(y)))


def put_snow(img, cx, top_y, spread, n, r):
    d = ImageDraw.Draw(img)
    ys = [top_y, top_y + r * 2.2, top_y]
    for i in range(n):
        x = cx - spread / 2 + (spread / (n - 1)) * i if n > 1 else cx
        y = ys[i % len(ys)]
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*SNOW, 255))
        d.ellipse([x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4], fill=(255, 255, 255, 255))


def put_bolt(img, cx, cy, size):
    d = ImageDraw.Draw(img)
    s = size
    pts = [
        (cx + s * 0.14, cy - s * 0.52),
        (cx - s * 0.30, cy + s * 0.08),
        (cx - s * 0.02, cy + s * 0.08),
        (cx - s * 0.16, cy + s * 0.60),
        (cx + s * 0.32, cy - s * 0.10),
        (cx + s * 0.03, cy - s * 0.10),
    ]
    d.polygon(pts, fill=(*BOLT, 255))


# ---- weather icons (transparent, 160px) ----------------------------------

def canvas(size):
    c = size * SS
    return Image.new("RGBA", (c, c), (0, 0, 0, 0)), c


def w_clear(size):
    img, c = canvas(size)
    put_sun(img, c * 0.5, c * 0.5, c * 0.23)
    return img


def w_partly(size):
    img, c = canvas(size)
    put_sun(img, c * 0.62, c * 0.38, c * 0.15)
    put_cloud(img, c * 0.45, c * 0.56, c * 0.52)
    return img


def w_cloudy(size):
    img, c = canvas(size)
    put_cloud(img, c * 0.58, c * 0.52, c * 0.40, top=GRAY_TOP, bot=GRAY_BOT, shadow=False)
    put_cloud(img, c * 0.44, c * 0.48, c * 0.50)
    return img


def w_fog(size):
    img, c = canvas(size)
    put_cloud(img, c * 0.5, c * 0.40, c * 0.5, shadow=False)
    d = ImageDraw.Draw(img)
    bh = c * 0.042
    for i in range(3):
        y = c * 0.66 + i * bh * 2.6
        w = c * 0.6 * (1 - i * 0.14)
        d.rounded_rectangle([c * 0.5 - w / 2, y, c * 0.5 + w / 2, y + bh],
                            radius=bh / 2, fill=(*FOG, 255))
    return img


def w_drizzle(size):
    img, c = canvas(size)
    put_cloud(img, c * 0.5, c * 0.40, c * 0.52)
    put_rain(img, c * 0.5, c * 0.66, c * 0.44, 3, c * 0.07, c * 0.13)
    return img


def w_rain(size):
    img, c = canvas(size)
    put_cloud(img, c * 0.5, c * 0.38, c * 0.54)
    put_rain(img, c * 0.5, c * 0.66, c * 0.5, 4, c * 0.075, c * 0.17)
    return img


def w_showers(size):
    img, c = canvas(size)
    put_sun(img, c * 0.66, c * 0.30, c * 0.12)
    put_cloud(img, c * 0.46, c * 0.46, c * 0.50)
    put_rain(img, c * 0.46, c * 0.72, c * 0.42, 3, c * 0.07, c * 0.15)
    return img


def w_snow(size):
    img, c = canvas(size)
    put_cloud(img, c * 0.5, c * 0.38, c * 0.54)
    put_snow(img, c * 0.5, c * 0.70, c * 0.44, 3, c * 0.05)
    return img


def w_storms(size):
    img, c = canvas(size)
    put_cloud(img, c * 0.5, c * 0.38, c * 0.54, top=GRAY_TOP, bot=GRAY_BOT)
    put_bolt(img, c * 0.5, c * 0.74, c * 0.5)
    return img


WEATHER = {
    "clear": w_clear, "partly_cloudy": w_partly, "cloudy": w_cloudy,
    "fog": w_fog, "drizzle": w_drizzle, "rain": w_rain, "showers": w_showers,
    "snow": w_snow, "thunderstorm": w_storms,
}


def gen_weather():
    for name, fn in WEATHER.items():
        fn(160).resize((160, 160), Image.LANCZOS).save(os.path.join(WX, f"{name}.png"))
    print("weather icons:", len(WEATHER))


# ---- app icons -----------------------------------------------------------

def scene_partly(img):
    """Draw the partly-cloudy motif centered/filling the given RGBA image."""
    W, H = img.size
    u = min(W, H)
    cx, cy = W * 0.5, H * 0.5
    put_sun(img, cx + u * 0.20, cy - u * 0.22, u * 0.17)
    put_cloud(img, cx - u * 0.10, cy + u * 0.12, u * 0.66)


def _font(size, bold=True):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _fit_font(draw, text, maxw, maxsize):
    size = maxsize
    while size > 8:
        f = _font(size, bold=True)
        b = draw.textbbox((0, 0), text, font=f)
        if (b[2] - b[0]) <= maxw:
            return f
        size -= 2
    return _font(8, bold=True)


def wordmark_tile(w, h):
    """Channel tile matching the dark app UI: weather glyph + 'Weather'.

    Designed for the 4:3 channel-poster aspect so it renders un-squished on
    both older and newer Roku home screens. Height-driven metrics so it also
    downscales cleanly to the small side-icon sizes.
    """
    cw, ch = w * SS, h * SS
    img = vgrad(cw, ch, (10, 20, 36), (22, 42, 70), ease=True)
    # subtle cyan glow accent (top-right), matching UI accents
    glow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gr = int(ch * 0.8)
    gd.ellipse([cw - gr, -gr // 2, cw + gr // 2, gr], fill=(56, 189, 248, 32))
    glow = glow.filter(ImageFilter.GaussianBlur(ch * 0.12))
    img = Image.alpha_composite(img, glow)

    # weather glyph (partly cloudy), centered upper area
    gcx, gcy = cw * 0.5, ch * 0.36
    put_sun(img, gcx + ch * 0.16, gcy - ch * 0.13, ch * 0.135)
    put_cloud(img, gcx - ch * 0.06, gcy + ch * 0.06, ch * 0.50)

    d = ImageDraw.Draw(img)
    text = "Weather"
    f = _fit_font(d, text, cw * 0.80, int(ch * 0.22))
    b = d.textbbox((0, 0), text, font=f)
    tw, th = b[2] - b[0], b[3] - b[1]
    tx = (cw - tw) / 2 - b[0]
    ty = ch * 0.62
    d.text((tx, ty), text, font=f, fill=(248, 250, 252, 255))

    # cyan underline accent
    uw = tw * 0.5
    uy = ty + th + ch * 0.055
    d.rounded_rectangle([cw / 2 - uw / 2, uy, cw / 2 + uw / 2, uy + ch * 0.022],
                        radius=ch * 0.011, fill=(56, 189, 248, 255))
    return img.resize((w, h), Image.LANCZOS)


def squircle(size, radius_frac=0.22):
    c = size * SS
    img = Image.new("RGBA", (c, c), (0, 0, 0, 0))
    grad = vgrad(c, c, (86, 168, 236), (128, 206, 246))
    mask = Image.new("L", (c, c), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, c - 1, c - 1],
                                           radius=int(c * radius_frac), fill=255)
    img.paste(grad, (0, 0), mask)
    # subtle top gloss
    gloss = Image.new("RGBA", (c, c), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).rounded_rectangle(
        [c * 0.06, c * 0.06, c * 0.94, c * 0.5], radius=int(c * 0.18),
        fill=(255, 255, 255, 30))
    img = Image.alpha_composite(img, gloss)
    scene_partly(img)
    return img.resize((size, size), Image.LANCZOS)


def gen_app_icons():
    # Focus icons at the 4:3 channel-poster aspect (fixes squish on older devices)
    wordmark_tile(540, 405).convert("RGB").save(os.path.join(IMG, "icon_focus_fhd.png"))
    wordmark_tile(290, 218).convert("RGB").save(os.path.join(IMG, "icon_focus_hd.png"))
    wordmark_tile(214, 144).convert("RGB").save(os.path.join(IMG, "icon_focus_sd.png"))
    # Side icons (legacy; provided for completeness)
    wordmark_tile(108, 69).convert("RGB").save(os.path.join(IMG, "icon_side_hd.png"))
    wordmark_tile(80, 46).convert("RGB").save(os.path.join(IMG, "icon_side_sd.png"))
    squircle(220).save(os.path.join(IMG, "brand_icon.png"))
    print("app icons done")


def gen_background():
    vgrad(1280, 720, (9, 18, 33), (17, 34, 58), ease=True).convert("RGB").save(
        os.path.join(IMG, "bg_gradient.png"))
    print("bg done")


def _splash(w, h):
    s = h / 720.0  # scale relative to the HD reference layout
    img = vgrad(w, h, (18, 52, 96), (36, 92, 150), ease=True)
    tile_sz = int(240 * s)
    tile = squircle(tile_sz)
    img.alpha_composite(tile, (w // 2 - tile_sz // 2, h // 2 - int(180 * s)))
    d = ImageDraw.Draw(img)
    try:
        tf = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", int(66 * s))
        sf = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", int(30 * s))
    except Exception:
        tf = ImageFont.load_default(); sf = tf
    for text, fnt, y, col in [("Weather", tf, h // 2 + int(96 * s), (248, 252, 255)),
                              ("7-Day Forecast", sf, h // 2 + int(172 * s), (210, 230, 248))]:
        b = d.textbbox((0, 0), text, font=fnt)
        d.text(((w - (b[2] - b[0])) // 2, y), text, font=fnt, fill=col)
    return img.convert("RGB")


def gen_splash():
    _splash(1920, 1080).save(os.path.join(IMG, "splash_fhd.png"))
    _splash(1280, 720).save(os.path.join(IMG, "splash_hd.png"))
    _splash(720, 480).save(os.path.join(IMG, "splash_sd.png"))
    print("splash done")


# ---- UI chrome -----------------------------------------------------------

def rrect(w, h, radius, fill, border=None, border_w=0):
    cw, ch = w * SS, h * SS
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=radius * SS, fill=fill)
    if border and border_w:
        d.rounded_rectangle([border_w * SS / 2, border_w * SS / 2,
                             cw - 1 - border_w * SS / 2, ch - 1 - border_w * SS / 2],
                            radius=radius * SS, outline=border, width=int(border_w * SS))
    return img.resize((w, h), Image.LANCZOS)


def rrect_glow(w, h, radius, fill, glow, border=None, border_w=0, glow_pad=10):
    cw, ch = w * SS, h * SS
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle([glow_pad * SS, glow_pad * SS, cw - 1 - glow_pad * SS,
                          ch - 1 - glow_pad * SS], radius=radius * SS, fill=glow)
    gl = gl.filter(ImageFilter.GaussianBlur(glow_pad * SS * 0.6))
    img = Image.alpha_composite(img, gl)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([glow_pad * SS, glow_pad * SS, cw - 1 - glow_pad * SS,
                         ch - 1 - glow_pad * SS], radius=radius * SS, fill=fill)
    if border and border_w:
        d.rounded_rectangle([glow_pad * SS, glow_pad * SS, cw - 1 - glow_pad * SS,
                             ch - 1 - glow_pad * SS], radius=radius * SS,
                            outline=border, width=int(border_w * SS))
    return img.resize((w, h), Image.LANCZOS)


def vgrad_rrect(w, h, radius, top, bottom):
    grad = vgrad(w * SS, h * SS, top, bottom)
    mask = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1],
                                           radius=radius * SS, fill=255)
    out = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out.resize((w, h), Image.LANCZOS)


def gen_chrome():
    rrect(640, 600, 34, (15, 23, 42, 232), border=(56, 189, 248, 40), border_w=2).save(
        os.path.join(UI, "panel.png"))
    rrect(96, 54, 15, (30, 41, 59, 255)).save(os.path.join(UI, "key.png"))
    rrect_glow(116, 74, 15, (56, 189, 248, 255), (56, 189, 248, 130), glow_pad=10).save(
        os.path.join(UI, "key_focus.png"))
    rrect(96, 54, 15, (14, 165, 233, 255)).save(os.path.join(UI, "key_action.png"))
    rrect(96, 54, 15, (30, 41, 59, 255)).save(os.path.join(UI, "key_del.png"))
    rrect(60, 74, 14, (15, 23, 42, 255)).save(os.path.join(UI, "digit.png"))
    rrect_glow(80, 94, 14, (17, 32, 56, 255), (56, 189, 248, 120),
               border=(56, 189, 248, 255), border_w=2, glow_pad=10).save(
        os.path.join(UI, "digit_active.png"))
    rrect(60, 74, 14, (17, 24, 39, 255), border=(51, 65, 85, 180), border_w=1).save(
        os.path.join(UI, "digit_filled.png"))
    vgrad_rrect(150, 412, 22, (30, 41, 61), (22, 32, 50)).save(os.path.join(UI, "card.png"))
    vgrad_rrect(150, 412, 22, (30, 74, 120), (20, 46, 82)).save(os.path.join(UI, "card_today.png"))

    spin = 100
    c = spin * SS
    img = Image.new("RGBA", (c, c), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wdt = int(c * 0.09)
    pad = wdt
    for i in range(0, 300, 4):
        a = i / 300.0
        d.arc([pad, pad, c - pad, c - pad], start=i, end=i + 6,
              fill=(56, 189, 248, int(30 + 225 * a)), width=wdt)
    img.resize((spin, spin), Image.LANCZOS).save(os.path.join(UI, "spinner.png"))
    print("chrome done")


if __name__ == "__main__":
    gen_weather()
    gen_app_icons()
    gen_background()
    gen_splash()
    gen_chrome()
    print("ALL DONE")
