import cv2
import numpy as np
from pathlib import Path

from . import draw
from . import filter
from . import hsv
from . import stack
from . import template
from . import text
from . import transform
from .input import wait_key, get_scaled_roi

with (Path(__file__).parent / './__version__').open() as f:
    __version__ = f.read()

def count_colors(image):
    reshaped = image.reshape(-1, image.shape[-1])
    return np.unique(reshaped, axis=0, return_counts=True)

def top_color(image, exclude=[(0,0,0), (255,255,255)]):
    colors, counts = count_colors(image)
    for count, color in sorted(zip(counts, colors.tolist()))[::-1]:
        b, g, r = color[:3]
        if not (b, g, r) in exclude:
            return (b, g, r)

def force_alpha(image):
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
    if image.shape[2] == 3:
        return np.dstack([image, np.full(image.shape[:2], 255, dtype=np.uint8)])
    return image

def replace_color(image, color1, color2):
    r1, g1, b1 = color1[:3]
    r2, g2, b2 = color2[:3]

    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    image[:,:,:3][mask] = [r2, g2, b2]


def remove_color_alpha(image, color1):
    r1, g1, b1 = color1

    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    image[mask] = [0, 0, 0, 0]