from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).with_name("neuro_symbolic_concept.png")
W, H = 1600, 980

COLORS = {
    "ink": "#17212b",
    "muted": "#52616f",
    "line": "#465a69",
    "blue_fill": "#eaf4ff",
    "blue": "#1f6fd1",
    "green_fill": "#eef9ef",
    "green": "#2f7d32",
    "orange_fill": "#fff6e7",
    "orange": "#f08c00",
    "purple_fill": "#f3f1ff",
    "purple": "#4955b8",
    "red": "#c92a2a",
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
    "heading": font(28, bold=True),
    "subheading": font(22, bold=True),
    "body": font(22),
    "small": font(18),
    "small_bold": font(18, bold=True),
    "arrow": font(19, italic=True),
}


def text_size(draw, text, font_obj):
    box = draw.textbbox((0, 0), text, font=font_obj)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, xy, text, fill, font_obj, line_spacing=8):
    x, y = xy
    lines = text.split("\n")
    heights = [text_size(draw, line, font_obj)[1] for line in lines]
    total_h = sum(heights) + line_spacing * (len(lines) - 1)
    cursor = y - total_h / 2
    for line, h in zip(lines, heights):
        w, _ = text_size(draw, line, font_obj)
        draw.text((x - w / 2, cursor), line, fill=fill, font=font_obj)
        cursor += h + line_spacing


def left_text(draw, xy, text, fill, font_obj, line_spacing=8):
    x, y = xy
    cursor = y
    for line in text.split("\n"):
        draw.text((x, cursor), line, fill=fill, font=font_obj)
        cursor += text_size(draw, line, font_obj)[1] + line_spacing


def wrapped_center(draw, box, text, fill, font_obj, width_chars, line_spacing=8):
    lines = []
    for para in text.split("\n"):
        lines.extend(wrap(para, width=width_chars))
    center_text(
        draw,
        ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2),
        "\n".join(lines),
        fill,
        font_obj,
        line_spacing,
    )


def rounded_box(draw, xy, fill, outline, width=3, radius=22):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


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


img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

center_text(d, (800, 62), "Neuro-Symbolic Framing of the Safety Layer", COLORS["ink"], F["title"])
center_text(
    d,
    (800, 105),
    "Combining flexible language interpretation with explicit clinical safety structure",
    COLORS["muted"],
    F["subtitle"],
)

rounded_box(d, (135, 165, 675, 525), COLORS["blue_fill"], COLORS["blue"], width=4)
center_text(d, (405, 215), "Neural Component", COLORS["blue"], F["heading"])
center_text(d, (405, 258), "LLM classifier", COLORS["ink"], F["subheading"])
left_text(
    d,
    (190, 315),
    "+ interprets free-form rescripting text\n+ handles ambiguity and context\n+ maps language to candidate labels\n- opaque and variable without constraints",
    COLORS["ink"],
    F["body"],
    line_spacing=14,
)

rounded_box(d, (925, 165, 1465, 525), COLORS["green_fill"], COLORS["green"], width=4)
center_text(d, (1195, 215), "Symbolic Component", COLORS["green"], F["heading"])
center_text(d, (1195, 258), "IRT knowledge graph", COLORS["ink"], F["subheading"])
left_text(
    d,
    (980, 315),
    "+ explicit clinical safety categories\n+ adaptive and maladaptive nodes\n+ correction edges toward mastery\n- requires interpretation of user text",
    COLORS["ink"],
    F["body"],
    line_spacing=14,
)

arrow(d, (405, 525), (690, 650), COLORS["line"], width=4)
arrow(d, (1195, 525), (910, 650), COLORS["line"], width=4)
center_text(d, (565, 590), "language understanding", COLORS["muted"], F["arrow"])
center_text(d, (1035, 590), "clinical structure", COLORS["muted"], F["arrow"])

rounded_box(d, (520, 650, 1080, 865), COLORS["purple_fill"], COLORS["purple"], width=4)
center_text(d, (800, 700), "Neuro-Symbolic Safety Layer", COLORS["purple"], F["heading"])
wrapped_center(
    d,
    (575, 735, 1025, 810),
    "Patient rescripting text -> graph node -> safety decision -> clinical correction",
    COLORS["ink"],
    F["body"],
    42,
)
center_text(
    d,
    (800, 830),
    "safe: proceed    unsafe: redirect via correction edge",
    COLORS["muted"],
    F["small_bold"],
)

rounded_box(d, (230, 905, 1370, 955), COLORS["orange_fill"], COLORS["orange"], width=3, radius=14)
center_text(
    d,
    (800, 930),
    "In this thesis: the LLM performs clinical entity linking; the knowledge graph supplies explicit IRT safety logic.",
    COLORS["orange"],
    F["small_bold"],
)

img.save(OUT, quality=95)
print(OUT)
