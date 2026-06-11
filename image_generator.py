import os
import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GENERATED_DIR = Path(__file__).parent / "generated"
GENERATED_DIR.mkdir(exist_ok=True)


def _find_font_fc(bold: bool) -> str:
    """Use fc-match (fontconfig) to find the best available font on any Linux."""
    try:
        query = "serif:bold" if bold else "serif"
        result = subprocess.run(
            ["fc-match", query, "--format=%{file}"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            if path and os.path.exists(path):
                return path
    except Exception:
        pass
    return ""


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a TrueType font — works on Debian, Ubuntu, NixOS (Railway) and macOS."""
    # 1. Try fontconfig (available everywhere when font packages are installed)
    fc_path = _find_font_fc(bold)
    if fc_path:
        try:
            return ImageFont.truetype(fc_path, size)
        except Exception:
            pass

    # 2. Hardcoded paths for Debian/Ubuntu
    debian_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"     if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"      if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/fonts-freefont-ttf/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/fonts-freefont-ttf/FreeSerif.ttf",
    ]
    for p in debian_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue

    # 3. Glob search in /nix/store (Railway NixOS)
    try:
        import glob
        suffix = "Bold.ttf" if bold else "Regular.ttf"
        nix_fonts = glob.glob(f"/nix/store/*/share/fonts/**/*{suffix}", recursive=True)
        for p in nix_fonts[:5]:
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    except Exception:
        pass

    # 4. Last resort — PIL built-in (no custom size)
    return ImageFont.load_default()


def _draw_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: tuple):
    points = []
    for i in range(360):
        angle = math.radians(i)
        x = size * (16 * math.sin(angle) ** 3)
        y = -size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        points.append((cx + x / 10, cy + y / 10))
    if len(points) > 2:
        draw.polygon(points, fill=color)


def generate_yes_image(crush_name: str, creator_name: str, date: str, time: str, link_id: str) -> str:
    W, H = 800, 600
    img = Image.new("RGBA", (W, H), (255, 248, 240, 255))
    draw = ImageDraw.ImageDraw(img)

    # Background gradient simulation with layered rects
    for i in range(H):
        ratio = i / H
        r = int(255 - ratio * 20)
        g = int(240 - ratio * 30)
        b = int(220 - ratio * 10)
        draw.line([(0, i), (W, i)], fill=(r, g, b, 255))

    # Paper texture dots
    rng = random.Random(42)
    for _ in range(400):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        alpha = rng.randint(10, 30)
        draw.ellipse([x, y, x + 2, y + 2], fill=(200, 180, 160, alpha))

    # Border
    draw.rectangle([10, 10, W - 10, H - 10], outline=(210, 160, 140, 200), width=3)
    draw.rectangle([16, 16, W - 16, H - 16], outline=(230, 180, 160, 150), width=1)

    # Corner decorations
    for cx, cy in [(30, 30), (W - 30, 30), (30, H - 30), (W - 30, H - 30)]:
        _draw_heart(draw, cx, cy, 8, (220, 80, 100, 200))

    # Floating hearts background
    heart_positions = [
        (100, 80, 5), (650, 120, 4), (200, 500, 6),
        (700, 480, 4), (400, 50, 7), (50, 300, 4),
        (750, 300, 5), (350, 560, 4),
    ]
    for hx, hy, hs in heart_positions:
        _draw_heart(draw, hx, hy, hs, (255, 150, 170, 100))

    # Envelope shape
    env_x, env_y, env_w, env_h = 340, 120, 120, 80
    draw.rectangle([env_x, env_y, env_x + env_w, env_y + env_h],
                   fill=(255, 230, 210, 200), outline=(200, 140, 120, 255), width=2)
    draw.polygon([(env_x, env_y), (env_x + env_w // 2, env_y + env_h // 2), (env_x + env_w, env_y)],
                 fill=(245, 210, 190, 200))
    _draw_heart(draw, env_x + env_w // 2, env_y + env_h // 2 + 15, 8, (220, 60, 80, 230))

    # Main title
    title_font = _get_font(42, bold=True)
    title = "SHE SAID YES!"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2 + 2, 222), title, font=title_font, fill=(180, 60, 80, 80))
    draw.text(((W - tw) // 2, 220), title, font=title_font, fill=(200, 50, 70, 255))

    # Crush name
    crush_font = _get_font(28, bold=True)
    crush_line = f"Crush Name: {crush_name}"
    bbox2 = draw.textbbox((0, 0), crush_line, font=crush_font)
    draw.text(((W - (bbox2[2] - bbox2[0])) // 2, 280), crush_line, font=crush_font, fill=(140, 60, 100, 255))

    # Creator
    creator_font = _get_font(22)
    creator_line = f"Created by: {creator_name}"
    bbox3 = draw.textbbox((0, 0), creator_line, font=creator_font)
    draw.text(((W - (bbox3[2] - bbox3[0])) // 2, 325), creator_line, font=creator_font, fill=(100, 60, 80, 220))

    # Divider
    draw.line([(200, 365), (600, 365)], fill=(200, 150, 160, 180), width=1)

    # Date / Time
    info_font = _get_font(18)
    date_line = f"Date: {date}    Time: {time}"
    bbox4 = draw.textbbox((0, 0), date_line, font=info_font)
    draw.text(((W - (bbox4[2] - bbox4[0])) // 2, 380), date_line, font=info_font, fill=(120, 80, 100, 200))

    # Congrats
    congrats_font = _get_font(20, bold=True)
    congrats = "Congratulations! Your crush accepted your proposal"
    bbox5 = draw.textbbox((0, 0), congrats, font=congrats_font)
    draw.text(((W - (bbox5[2] - bbox5[0])) // 2, 430), congrats, font=congrats_font, fill=(160, 60, 80, 230))

    # Bottom heart row
    for hx in range(200, 600, 50):
        _draw_heart(draw, hx, 490, 5, (220, 100, 120, 180))

    # Soft glow overlay on title area
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W // 2 - 160, 200, W // 2 + 160, 280], fill=(255, 200, 200, 30))
    blurred = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, blurred)

    out_path = GENERATED_DIR / f"{link_id}_yes.png"
    img.convert("RGB").save(str(out_path), "PNG", quality=95)
    return str(out_path)
