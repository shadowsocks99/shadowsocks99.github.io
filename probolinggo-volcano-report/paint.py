# -*- coding: utf-8 -*-
"""Procedurally paint oil-painting style illustrations for the
Probolinggo (Bromo-Tengger) volcano field report."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)

W, H = 1600, 1000


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, w, h, stops):
    """Vertical gradient given [(y_ratio, color), ...]."""
    for y in range(h):
        t = y / h
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= t <= y1:
                tt = (t - y0) / max(y1 - y0, 1e-6)
                draw.line([(0, y), (w, y)], fill=lerp(c0, c1, tt))
                break


def painterly(base, strokes=55000, lmin=10, lmax=30, wmin=3, wmax=9,
              jitter=16, blur=5):
    """Re-render a base image as overlapping brush strokes."""
    w, h = base.size
    out = base.filter(ImageFilter.GaussianBlur(blur)).convert('RGB')
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    px = base.convert('RGB').load()
    for _ in range(strokes):
        x, y = random.randrange(w), random.randrange(h)
        r, g, b = px[x, y]
        j = lambda c: max(0, min(255, c + random.randint(-jitter, jitter)))
        col = (j(r), j(g), j(b), random.randint(150, 230))
        ang = random.uniform(-0.45, 0.45)  # mostly horizontal strokes
        if random.random() < 0.18:
            ang += math.pi / 2 * random.choice([1, -1]) * random.uniform(0.3, 1)
        ln = random.uniform(lmin, lmax)
        dx, dy = math.cos(ang) * ln / 2, math.sin(ang) * ln / 2
        d.line([(x - dx, y - dy), (x + dx, y + dy)],
               fill=col, width=int(random.uniform(wmin, wmax)))
    out.paste(layer, (0, 0), layer)
    return out


def canvas_weave(img, strength=14):
    """Overlay a woven-canvas texture."""
    w, h = img.size
    tex = Image.new('L', (w, h), 128)
    d = ImageDraw.Draw(tex)
    for y in range(0, h, 3):
        v = 128 + int(strength * math.sin(y * 1.7)) + random.randint(-6, 6)
        d.line([(0, y), (w, y)], fill=v)
    for x in range(0, w, 3):
        v = 128 + int(strength * 0.7 * math.sin(x * 1.3)) + random.randint(-5, 5)
        d.line([(x, 0), (x, h)], fill=v)
    tex = tex.filter(ImageFilter.GaussianBlur(0.6))
    out = img.convert('RGB')
    opx, tpx = out.load(), tex.load()
    for y in range(h):
        for x in range(w):
            f = (tpx[x, y] - 128) / 128 * 0.18
            r, g, b = opx[x, y]
            opx[x, y] = (max(0, min(255, int(r * (1 + f)))),
                         max(0, min(255, int(g * (1 + f)))),
                         max(0, min(255, int(b * (1 + f)))))
    return out


def vignette(img, amount=0.35):
    w, h = img.size
    mask = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w * 0.25, -h * 0.25, w * 1.25, h * 1.25], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(180))
    dark = Image.eval(img.convert('RGB'), lambda v: int(v * (1 - amount)))
    return Image.composite(img.convert('RGB'), dark, mask)


def cone(d, cx, base_y, top_y, half_base, half_top, color):
    d.polygon([(cx - half_base, base_y), (cx - half_top, top_y),
               (cx + half_top, top_y), (cx + half_base, base_y)], fill=color)


def smoke(d, cx, top_y, n=140, spread=90, rise=420, col=(225, 218, 205)):
    for i in range(n):
        t = i / n
        x = cx + random.uniform(-1, 1) * spread * (0.25 + t) + t * 60
        y = top_y - t * rise + random.uniform(-22, 22)
        r = random.uniform(14, 46) * (0.45 + t)
        a = int(120 * (1 - t * 0.75))
        c = lerp(col, (245, 242, 235), t)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (a,))


# ---------------------------------------------------------------- scene 1
# Cover: Bromo & Batok at sunrise from the caldera rim
def scene_cover():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img, 'RGBA')
    vgrad(d, W, H, [(0.0, (38, 26, 64)), (0.30, (104, 52, 88)),
                    (0.46, (214, 116, 62)), (0.56, (246, 186, 92)),
                    (0.62, (200, 140, 90)), (1.0, (74, 56, 48))])
    # sun glow
    for r, a in [(260, 26), (180, 40), (110, 70), (60, 130)]:
        d.ellipse([W * 0.70 - r, H * 0.52 - r, W * 0.70 + r, H * 0.52 + r],
                  fill=(255, 214, 130, a))
    d.ellipse([W * 0.70 - 34, H * 0.52 - 34, W * 0.70 + 34, H * 0.52 + 34],
              fill=(255, 238, 190))
    # distant caldera wall + Semeru on horizon
    d.polygon([(0, H * 0.60), (W * 0.18, H * 0.50), (W * 0.34, H * 0.555),
               (W * 0.52, H * 0.485), (W * 0.62, H * 0.55), (W * 0.80, H * 0.50),
               (W, H * 0.565), (W, H * 0.62), (0, H * 0.62)],
              fill=(64, 42, 70))
    cone(d, W * 0.86, H * 0.56, H * 0.40, W * 0.10, W * 0.012, (52, 34, 60))
    smoke(d, W * 0.864, H * 0.40, n=60, spread=30, rise=150, col=(150, 130, 140))
    # Batok (ridged, dormant cone)
    cone(d, W * 0.56, H * 0.78, H * 0.46, W * 0.17, W * 0.035, (66, 48, 44))
    for i in range(14):  # ridges
        t = i / 13
        x0 = W * 0.56 - W * 0.155 + t * W * 0.31
        x1 = W * 0.56 - W * 0.030 + t * W * 0.062
        d.line([(x1, H * 0.465), (x0, H * 0.775)], fill=(96, 72, 58, 160), width=7)
    # Bromo (active crater)
    cone(d, W * 0.30, H * 0.82, H * 0.535, W * 0.21, W * 0.075, (82, 58, 46))
    d.ellipse([W * 0.30 - W * 0.075, H * 0.520, W * 0.30 + W * 0.075, H * 0.553],
              fill=(48, 34, 30))
    for i in range(10):
        t = i / 9
        x0 = W * 0.30 - W * 0.19 + t * W * 0.38
        x1 = W * 0.30 - W * 0.068 + t * W * 0.136
        d.line([(x1, H * 0.545), (x0, H * 0.815)], fill=(116, 86, 62, 130), width=8)
    smoke(d, W * 0.30, H * 0.525, n=150, spread=80, rise=380)
    # sand sea with morning mist
    d.rectangle([0, H * 0.80, W, H], fill=(96, 78, 64))
    for i in range(40):
        y = H * (0.80 + 0.2 * random.random())
        x = random.uniform(0, W)
        ln = random.uniform(90, 380)
        c = lerp((70, 56, 48), (150, 122, 92), random.random())
        d.line([(x, y), (x + ln, y + random.uniform(-6, 6))], fill=c + (170,),
               width=random.randint(4, 12))
    for i in range(26):  # mist
        x, y = random.uniform(0, W), H * random.uniform(0.74, 0.84)
        r = random.uniform(60, 190)
        d.ellipse([x - r, y - r * 0.28, x + r, y + r * 0.28],
                  fill=(232, 214, 196, random.randint(26, 60)))
    out = painterly(img, strokes=62000)
    return canvas_weave(vignette(out))


# ---------------------------------------------------------------- scene 2
# The Sand Sea (Laut Pasir / Segara Wedi)
def scene_sandsea():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img, 'RGBA')
    vgrad(d, W, H, [(0.0, (168, 188, 208)), (0.38, (212, 206, 188)),
                    (0.46, (188, 168, 140)), (1.0, (110, 92, 72))])
    # caldera wall
    d.polygon([(0, H * 0.46), (W * 0.2, H * 0.34), (W * 0.45, H * 0.44),
               (W * 0.7, H * 0.32), (W, H * 0.42), (W, H * 0.50), (0, H * 0.50)],
              fill=(86, 92, 70))
    for i in range(260):  # scrubby green on the wall
        x = random.uniform(0, W)
        y = H * random.uniform(0.34, 0.50)
        r = random.uniform(4, 16)
        c = lerp((60, 76, 44), (118, 128, 70), random.random())
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=c + (200,))
    # flat ash plain with wind-swept furrows
    d.rectangle([0, H * 0.50, W, H], fill=(132, 112, 88))
    for i in range(90):
        t = random.random()
        y = H * (0.50 + 0.5 * t * t)
        x = random.uniform(-100, W)
        ln = random.uniform(160, 620) * (0.4 + t)
        c = lerp((90, 74, 60), (176, 150, 116), random.random())
        d.line([(x, y), (x + ln, y + random.uniform(-10, 10))], fill=c + (180,),
               width=random.randint(4, 14))
    # walking surveyors with packs
    for (px_, py_, s) in [(W * 0.42, H * 0.80, 1.0), (W * 0.47, H * 0.815, 0.92),
                          (W * 0.52, H * 0.79, 0.85)]:
        hgt = 64 * s
        d.line([(px_, py_), (px_, py_ - hgt)], fill=(40, 30, 26), width=int(10 * s))
        d.ellipse([px_ - 8 * s, py_ - hgt - 14 * s, px_ + 8 * s, py_ - hgt + 2 * s],
                  fill=(40, 30, 26))
        d.ellipse([px_ - 14 * s, py_ - hgt + 8 * s, px_ + 2 * s, py_ - hgt + 34 * s],
                  fill=(122, 60, 38))  # red pack
        d.ellipse([px_ - 26 * s, py_ - 4, px_ + 26 * s, py_ + 8],
                  fill=(60, 48, 40, 140))  # shadow
    # dust haze
    for i in range(20):
        x, y = random.uniform(0, W), H * random.uniform(0.46, 0.60)
        r = random.uniform(80, 220)
        d.ellipse([x - r, y - r * 0.25, x + r, y + r * 0.25],
                  fill=(225, 210, 188, random.randint(20, 48)))
    out = painterly(img, strokes=58000)
    return canvas_weave(vignette(out, 0.30))


# ---------------------------------------------------------------- scene 3
# Looking into the Bromo crater
def scene_crater():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img, 'RGBA')
    vgrad(d, W, H, [(0.0, (196, 178, 160)), (0.35, (170, 148, 128)),
                    (1.0, (84, 62, 50))])
    # outer slopes
    d.polygon([(0, H), (0, H * 0.42), (W * 0.5, H * 0.30), (W, H * 0.40), (W, H)],
              fill=(108, 82, 60))
    # crater bowl
    d.ellipse([W * 0.08, H * 0.34, W * 0.92, H * 1.05], fill=(70, 52, 42))
    d.ellipse([W * 0.20, H * 0.46, W * 0.80, H * 0.98], fill=(46, 34, 30))
    d.ellipse([W * 0.34, H * 0.60, W * 0.66, H * 0.92], fill=(30, 22, 20))
    # sulfur stains
    for i in range(120):
        a = random.uniform(0, 2 * math.pi)
        rr = random.uniform(0.18, 0.40)
        x = W * 0.5 + math.cos(a) * W * rr
        y = H * 0.70 + math.sin(a) * H * rr * 0.55
        r = random.uniform(6, 26)
        c = lerp((188, 168, 96), (226, 206, 130), random.random())
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=c + (130,))
    # radial gullies on inner wall
    for i in range(60):
        a = random.uniform(0, 2 * math.pi)
        x0 = W * 0.5 + math.cos(a) * W * 0.16
        y0 = H * 0.72 + math.sin(a) * H * 0.12
        x1 = W * 0.5 + math.cos(a) * W * 0.40
        y1 = H * 0.70 + math.sin(a) * H * 0.30
        c = lerp((130, 100, 72), (60, 44, 36), random.random())
        d.line([(x0, y0), (x1, y1)], fill=c + (150,), width=random.randint(4, 10))
    # rising steam column
    smoke(d, W * 0.5, H * 0.66, n=240, spread=130, rise=560, col=(228, 222, 212))
    # rim figures
    for (px_, s) in [(W * 0.13, 0.9), (W * 0.165, 1.0)]:
        py_ = H * 0.40
        d.line([(px_, py_), (px_, py_ - 52 * s)], fill=(34, 26, 24), width=9)
        d.ellipse([px_ - 7, py_ - 52 * s - 13, px_ + 7, py_ - 52 * s + 1],
                  fill=(34, 26, 24))
    out = painterly(img, strokes=58000)
    return canvas_weave(vignette(out, 0.32))


# ---------------------------------------------------------------- scene 4
# Tengger highland village & terraced fields (Cemoro Lawang)
def scene_village():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img, 'RGBA')
    vgrad(d, W, H, [(0.0, (150, 176, 198)), (0.30, (208, 212, 198)),
                    (0.42, (170, 178, 140)), (1.0, (66, 88, 52))])
    # far volcano
    cone(d, W * 0.78, H * 0.42, H * 0.20, W * 0.16, W * 0.02, (96, 92, 110))
    smoke(d, W * 0.782, H * 0.20, n=70, spread=36, rise=170, col=(210, 205, 200))
    # terraced slope
    for i in range(9):
        t = i / 8
        y = H * (0.42 + 0.58 * t * t)
        col = lerp((96, 122, 60), (52, 78, 42), random.random())
        d.polygon([(0, y), (W, y - H * 0.03), (W, H), (0, H)], fill=col)
        d.line([(0, y), (W, y - H * 0.03)], fill=(40, 56, 34), width=6)
    # crop rows
    for i in range(70):
        y = H * random.uniform(0.46, 0.98)
        x = random.uniform(-50, W)
        ln = random.uniform(120, 420)
        c = lerp((120, 150, 70), (44, 66, 38), random.random())
        d.line([(x, y), (x + ln, y - ln * 0.03)], fill=c + (200,),
               width=random.randint(5, 12))
    # village houses with warm roofs
    for (hx, hy, s) in [(W * 0.18, H * 0.52, 1.0), (W * 0.26, H * 0.50, 0.85),
                        (W * 0.33, H * 0.53, 0.9), (W * 0.12, H * 0.56, 1.1),
                        (W * 0.42, H * 0.51, 0.7)]:
        bw, bh = 70 * s, 40 * s
        d.rectangle([hx - bw / 2, hy - bh, hx + bw / 2, hy], fill=(196, 182, 158))
        d.polygon([(hx - bw * 0.62, hy - bh), (hx, hy - bh - 30 * s),
                   (hx + bw * 0.62, hy - bh)], fill=(150, 64, 44))
    # cypress-like trees
    for i in range(16):
        x = random.uniform(0, W)
        y = H * random.uniform(0.44, 0.60)
        s = random.uniform(0.6, 1.2)
        d.polygon([(x - 9 * s, y), (x, y - 46 * s), (x + 9 * s, y)],
                  fill=(34, 52, 36))
    out = painterly(img, strokes=56000)
    return canvas_weave(vignette(out, 0.28))


# ---------------------------------------------------------------- paper bg
def paper():
    w, h = 800, 1130
    img = Image.new('RGB', (w, h), (243, 234, 215))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(2600):
        x, y = random.randrange(w), random.randrange(h)
        r = random.uniform(1, 5)
        c = random.choice([(228, 214, 188), (250, 243, 228), (236, 224, 200)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (60,))
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], fill=(225, 212, 186, 26))
    for x in range(0, w, 4):
        d.line([(x, 0), (x, h)], fill=(232, 220, 196, 22))
    # darkened edges
    edge = Image.new('L', (w, h), 0)
    de = ImageDraw.Draw(edge)
    de.rectangle([26, 26, w - 26, h - 26], fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(40))
    dark = Image.eval(img, lambda v: int(v * 0.90))
    return Image.composite(img, dark, edge)


if __name__ == '__main__':
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    os.makedirs(out, exist_ok=True)
    jobs = [('cover.jpg', scene_cover), ('sandsea.jpg', scene_sandsea),
            ('crater.jpg', scene_crater), ('village.jpg', scene_village)]
    for name, fn in jobs:
        print('painting', name, '...')
        fn().save(os.path.join(out, name), quality=92)
    print('painting paper.jpg ...')
    paper().save(os.path.join(out, 'paper.jpg'), quality=90)
    print('done')
