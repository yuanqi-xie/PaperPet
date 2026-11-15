"""Generate PaperPet icon assets from the supplied artwork (assets/icon-art.png).

The artwork is a cream tile with the reading cat. We keep that composition,
trim only the empty margin, square it, scale it and round the corners so the
icon fills the whole shortcut frame at every size.
"""

from PIL import Image, ImageChops, ImageDraw

INK = (34, 48, 58, 255)
CREAM = (247, 240, 223, 255)
BLUE = (47, 95, 138, 255)

SOURCE = "assets/icon-art.png"
SIZE = 1024
RADIUS = 0.20  # share of the tile, matching Windows 11 rounded tiles
PAD = 0.04  # breathing room around the drawing, share of its long side
# The artwork's paper is #FDFDF1 (almost white), which reads as white in a
# 32-48px icon. Multiplying by this keeps the cat and its shadows intact but
# lands the tile on a visible 米色 (#F7F0E2).
TINT = (249, 242, 239)


def warm(img):
    return ImageChops.multiply(img, Image.new("RGB", img.size, TINT))


def background(rgb):
    w, h = rgb.size
    px = rgb.load()
    return px[2, 2] if rgb.mode == "RGB" else tuple(rgb.getpixel((2, 2)))


def square(img):
    """Center the artwork on a square canvas without zooming it."""
    w, h = img.size
    side = min(w, h)
    if w == h:
        return img
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def rounded(img_rgb):
    big = img_rgb.resize((SIZE, SIZE), Image.LANCZOS).convert("RGBA")
    radius = int(SIZE * RADIUS)
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=radius, fill=255)
    big.putalpha(mask)
    edge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle(
        (1, 1, SIZE - 2, SIZE - 2), radius=radius, outline=(34, 48, 58, 30), width=4
    )
    big = Image.alpha_composite(big, edge)
    big.putalpha(ImageChops.multiply(big.getchannel("A"), mask))
    return big


art = warm(Image.open(SOURCE).convert("RGB"))
icon = rounded(square(art))

icon.resize((512, 512), Image.LANCZOS).save("assets/icon.png")
icon.resize((256, 256), Image.LANCZOS).save("assets/icon-256.png")
icon.save(
    "assets/icon.ico",
    format="ICO",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
icon.resize((96, 96), Image.LANCZOS).save("zotero-plugin/icon.png")

# Tray: transparent, simple face so it stays readable at 16px on the taskbar
tray = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
td = ImageDraw.Draw(tray)
td.rounded_rectangle((7, 14, 57, 57), radius=18, fill=CREAM, outline=INK, width=3)
td.polygon([(12, 17), (11, 5), (24, 13)], fill=CREAM, outline=INK, width=2)
td.polygon([(52, 17), (53, 5), (40, 13)], fill=CREAM, outline=INK, width=2)
td.ellipse((16, 24, 30, 38), outline=BLUE, width=3)
td.ellipse((34, 24, 48, 38), outline=BLUE, width=3)
td.line((29, 31, 35, 31), fill=BLUE, width=2)
td.ellipse((21, 29, 24, 34), fill=INK)
td.ellipse((40, 29, 43, 34), fill=INK)
td.arc((25, 33, 39, 45), 20, 160, fill=INK, width=2)
tray.resize((32, 32), Image.LANCZOS).save("assets/tray.png")
print("icons written")
