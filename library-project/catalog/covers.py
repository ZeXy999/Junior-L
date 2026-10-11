"""Generate book cover images with Pillow (no external services or downloads needed)."""
import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 400, 600

PALETTES = {
    "Romance": ((200, 74, 110), (88, 24, 62)),
    "Gothic & Horror": ((70, 40, 84), (14, 10, 24)),
    "Adventure": ((22, 118, 138), (8, 38, 72)),
    "Classic Fiction": ((184, 134, 64), (70, 44, 22)),
    "Historical": ((134, 84, 58), (46, 28, 26)),
    "Fantasy": ((100, 68, 184), (30, 20, 86)),
    "Science Fiction": ((24, 158, 168), (8, 30, 62)),
    "Mystery": ((66, 78, 100), (16, 20, 32)),
    "Children's": ((240, 154, 64), (184, 62, 42)),
}
DEFAULT_PALETTE = ((74, 94, 146), (20, 30, 62))

_BOLD = ["DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
         "georgiab.ttf", "timesbd.ttf", "Georgia Bold.ttf", "Times New Roman Bold.ttf",
         "/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "arialbd.ttf",
         "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
_REGULAR = ["DejaVuSerif.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "georgia.ttf", "times.ttf", "Georgia.ttf", "Times New Roman.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf", "arial.ttf",
            "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def _font(size, bold=True):
    for name in (_BOLD if bold else _REGULAR):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_cover(title, authors, genre_name="", seed_key=""):
    """Return JPEG bytes for a 400x600 cover."""
    rng = random.Random(f"{seed_key}{title}")
    top, bottom = PALETTES.get(genre_name, DEFAULT_PALETTE)
    # vary the colours a little so books in one genre don't look identical
    shift = rng.randint(-22, 22)
    top = tuple(max(0, min(255, c + shift)) for c in top)
    bottom = tuple(max(0, min(255, c - shift // 2)) for c in bottom)

    image = Image.new("RGB", (WIDTH, HEIGHT), top)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        draw.line([(0, y), (WIDTH, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))

    # decorative translucent shapes
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    style = rng.choice(["circles", "stripes", "arcs"])
    if style == "circles":
        for _ in range(7):
            r = rng.randint(40, 150)
            x, y = rng.randint(-20, WIDTH + 20), rng.randint(-20, HEIGHT + 20)
            odraw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(14, 34)))
    elif style == "stripes":
        for k in range(-HEIGHT, WIDTH, rng.randint(36, 58)):
            odraw.polygon([(k, HEIGHT), (k + 22, HEIGHT), (k + 22 + HEIGHT, 0), (k + HEIGHT, 0)],
                          fill=(255, 255, 255, rng.randint(12, 26)))
    else:
        for i in range(6):
            r = 90 + i * 55
            odraw.arc([WIDTH // 2 - r, HEIGHT - 80 - r, WIDTH // 2 + r, HEIGHT - 80 + r],
                      200, 340, fill=(255, 255, 255, 60), width=3)
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image)

    # frame
    draw.rectangle([18, 18, WIDTH - 18, HEIGHT - 18], outline=(255, 255, 255, 150), width=2)
    draw.rectangle([26, 26, WIDTH - 26, HEIGHT - 26], outline=(255, 255, 255, 70), width=1)

    # genre label
    if genre_name:
        label_font = _font(14, bold=False)
        label = genre_name.upper()
        draw.text((WIDTH / 2, 62), label, font=label_font, fill=(255, 255, 255, 200), anchor="mm")

    # title: shrink until it fits in at most 6 lines
    max_w = WIDTH - 90
    size = 46
    while True:
        font = _font(size)
        lines = _wrap(draw, title, font, max_w)
        if len(lines) <= 6 or size <= 22:
            break
        size -= 3
    line_h = int(size * 1.22)
    total = line_h * len(lines)
    y = 120 + max(0, (270 - total) // 2)
    for line in lines:
        draw.text((WIDTH / 2 + 2, y + 2), line, font=font, fill=(0, 0, 0, 90), anchor="ma")
        draw.text((WIDTH / 2, y), line, font=font, fill=(255, 255, 255, 255), anchor="ma")
        y += line_h

    # divider + author
    draw.line([(WIDTH / 2 - 40, HEIGHT - 150), (WIDTH / 2 + 40, HEIGHT - 150)], fill=(255, 255, 255, 200), width=2)
    a_font = _font(24, bold=False)
    a_lines = _wrap(draw, authors, a_font, max_w)[:2]
    ay = HEIGHT - 128
    for line in a_lines:
        draw.text((WIDTH / 2, ay), line, font=a_font, fill=(255, 255, 255, 235), anchor="ma")
        ay += 32

    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()
