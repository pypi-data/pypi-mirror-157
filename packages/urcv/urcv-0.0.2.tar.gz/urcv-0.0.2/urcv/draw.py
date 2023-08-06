import cv2
import numpy as np


def polygon(image, points, fill=None, stroke=None, interiors=[], bg=None):
    pts = np.array(points, dtype=np.int32)
    pts = pts.reshape((-1,1,2))
    if fill is not None:
        cv2.fillPoly(image, [pts], color=fill)
    if stroke is not None:
        cv2.polylines(image, [pts], True, color=stroke)
    if bg is None:
        bg = tuple([0 for _ in fill])
    for shape in interiors:
        polygon(image, shape, fill=bg, stroke=stroke)


def paste(back, front, x1, y1):
    """
    Paste front onto back at x, y
    Optimized for non-alpha images
    """

    # if x or y is negative, cut front to fit
    if x1 < 0:
        front = front[:,abs(x1):]
        x1 = 0
    if y1 < 0:
        front = front[abs(y1):]
        y1 = 0

    bh, bw = back.shape[:2]
    fh, fw = front.shape[:2]
    x2 = x1+fw
    y2 = y1+fh

    # if x or y overflows right or bottom edges, cut front to fit
    if x2 > bw:
        dx = x2 - bw
        x2 = bw
        front = front[:,:-dx]
    if y2 > bh:
        dy = y2 - bh
        y2 = bh
        front = front[:-dy]

    back[y1:y2, x1:x2] = front


def paste_alpha(back, front, x, y):
    """
    Paste front onto back at x, y while preserving alpha channel
    Will throw error if target is out of bounds for back image
    """
    assert back.shape[2] == 4
    if front.shape[2] == 3:
        front = cv2.cvtColor(back, cv2.COLOR_BGR2BGRA)

    if x < 0:
        front = front[:, abs(x):]
        x = 0

    if y < 0:
        front = front[abs(y):]
        y = 0

    y_buffer = back.shape[0] - front.shape[0] - y
    if y_buffer < 0:
        front = front[:y_buffer]

    x_buffer = back.shape[1] - front.shape[1] - x
    if x_buffer < 0:
        front = front[:,:-x_buffer]

    # crop the overlay from both images
    bh, bw = back.shape[:2]
    fh, fw = front.shape[:2]
    x1, x2 = max(x, 0), min(x+fw, bw)
    y1, y2 = max(y, 0), min(y+fh, bh)
    back_cropped = back[y1:y2, x1:x2]

    alpha_front = front[:,:,3:4] / 255
    alpha_back = back_cropped[:,:,3:4] / 255

    # replace an area in back with overlay
    back[y1:y2, x1:x2, :3] = alpha_front * front[:,:,:3] + (1-alpha_front) * back_cropped[:,:,:3]
    back[y1:y2, x1:x2, 3:4] = (alpha_front + alpha_back) / (1 + alpha_front*alpha_back) * 255
