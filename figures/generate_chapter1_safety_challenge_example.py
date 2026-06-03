from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).with_name("chapter1_safety_challenge_example.png")
W, H = 1600, 980

COLORS = {
    "ink": "#17212b",
    "muted": "#52616f",
    "blue_fill": "#eaf4ff",
    "blue": "#1f6fd1",
    "purple_fill": "#f3f1ff",
    "purple": "#4955b8",
    "red_fill": "#fff0f0",
    "red": "#c92a2a",
    "red_dark": "#b42318",
    "green_fill": "#eef9ef",
    "green": "#2f7d32",
    "green_dark": "#1b6e2a",
    "orange_fill": "#fff6e7",
    "orange": "#f08c00",
    "orange_dark": "#c05600",
    "line": "#465a69",
}


def font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/Library/Fonts/Arial Bold.ttf",
            ]
        )
    elif italic:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
                "/Library/Fonts/Arial Italic.ttf",
            ]
        )
    candidates.extend(
        [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


F = {
    "title": font(38, bold=True),
    "subtitle": font(24),
    "label": font(25, bold=True),
    "small_label": font(20, bold=True),
    "body": font(22),
    "small": font(18),
    "note": font(20, bold=True),
    "arrow": font(19, italic=True),
}


def center_text(draw, xy, text, fill, font_obj, line_spacing=8):
    x, y = xy
    lines = text.split("\n")
    total_h = sum(draw.textbbox((0, 0), line, font=font_obj)[3] for line in lines)
    total_h += line_spacing * (len(lines) - 1)
    cursor = y - total_h / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        draw.text((x - (bbox[2] - bbox[0]) / 2, cursor), line, fill=fill, font=font_obj)
        cursor += (bbox[3] - bbox[1]) + line_spacing


def wrapped_center(draw, box, text, fill, font_obj, width_chars, line_spacing=7):
    x0, y0, x1, y1 = box
    lines = []
    for para in text.split("\n"):
        lines.extend(wrap(para, width=width_chars))
    center_text(draw, ((x0 + x1) / 2, (y0 + y1) / 2), "\n".join(lines), fill, font_obj, line_spacing)


def arrow(draw, start, end, fill, width=4):
    draw.line([start, end], fill=fill, width=width)
    x0, y0 = start
    x1, y1 = end
    dx, dy = x1 - x0, y1 - y0
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    size = 18
    back = (x1 - ux * size, y1 - uy * size)
    p1 = (back[0] + px * size * 0.55, back[1] + py * size * 0.55)
    p2 = (back[0] - px * size * 0.55, back[1] - py * size * 0.55)
    draw.polygon([(x1, y1), p1, p2], fill=fill)


def rounded_box(draw, xy, fill, outline, width=3, radius=20):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

center_text(d, (800, 62), "Example of the Safety Problem in AI-Assisted IRT", COLORS["ink"], F["title"])
center_text(
    d,
    (800, 105),
    "The same rescripting attempt can be validated by a baseline LLM or redirected by a clinical safety layer",
    COLORS["muted"],
    F["subtitle"],
)

rounded_box(d, (330, 155, 1270, 305), COLORS["blue_fill"], COLORS["blue"])
center_text(d, (800, 197), "Nightmare Context", COLORS["blue"], F["label"])
center_text(
    d,
    (800, 252),
    '"I am running through a dark forest.\nSomething is chasing me and getting closer."',
    COLORS["ink"],
    F["body"],
)

arrow(d, (800, 305), (800, 355), COLORS["line"])

rounded_box(d, (305, 355, 1295, 520), COLORS["purple_fill"], COLORS["purple"])
center_text(d, (800, 398), "Patient Rescripting Attempt", COLORS["ink"], F["label"])
center_text(
    d,
    (800, 455),
    '"I hide behind a tree and wait until the threat disappears.\nI try to make myself small so it does not notice me."',
    COLORS["ink"],
    F["body"],
)
center_text(
    d,
    (800, 497),
    "Clinically subtle: the response sounds safe, but rehearses avoidance and passivity.",
    COLORS["orange_dark"],
    F["small"],
)

d.line([(800, 520), (800, 575)], fill=COLORS["line"], width=4)
arrow(d, (800, 575), (435, 635), COLORS["red"])
arrow(d, (800, 575), (1165, 635), COLORS["green"])
center_text(d, (610, 586), "baseline LLM", COLORS["red"], F["arrow"])
center_text(d, (995, 586), "LLM + safety layer", COLORS["green"], F["arrow"])

rounded_box(d, (115, 635, 705, 855), COLORS["red_fill"], COLORS["red"], width=4)
center_text(d, (410, 677), "Without Explicit Safety Layer", COLORS["red_dark"], F["label"])
wrapped_center(
    d,
    (155, 705, 665, 800),
    '"That sounds like a good way to protect yourself. Imagine the tree hiding you completely until the danger is gone."',
    COLORS["ink"],
    F["body"],
    48,
)
center_text(d, (410, 821), "Problem: reinforces avoidance", COLORS["red_dark"], F["note"])

rounded_box(d, (895, 635, 1485, 855), COLORS["green_fill"], COLORS["green"], width=4)
center_text(d, (1190, 677), "With Clinical Safety Layer", COLORS["green_dark"], F["label"])
wrapped_center(
    d,
    (935, 705, 1445, 800),
    '"It makes sense to want safety. In the dream, you can also have agency: what if you turned to face what is chasing you?"',
    COLORS["ink"],
    F["body"],
    48,
)
center_text(d, (1190, 821), "Correction: redirects toward behavioral mastery", COLORS["green_dark"], F["note"])

rounded_box(d, (230, 885, 1370, 947), COLORS["orange_fill"], COLORS["orange"], width=3, radius=14)
center_text(
    d,
    (800, 916),
    "Safety-layer interpretation: Avoidance detected -> correction edge -> Behavioral Mastery",
    COLORS["orange_dark"],
    F["small_label"],
)

img.save(OUT, quality=95)
print(OUT)
