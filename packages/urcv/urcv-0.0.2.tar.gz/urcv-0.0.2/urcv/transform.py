import cv2
import numpy as np


def autocrop_zeros(image):
    image = image.copy()
    while np.sum(image[-1]) == 0:
        # bottom
        image = image[:-1]
    while np.sum(image[0]) == 0:
        # top
        image = image[1:]
    while np.sum(image[:,-1]) == 0:
        # right
        image = image[:,:-1]
    while np.sum(image[:,0]) == 0:
        # left
        image = image[:,1:]
    return image


def scale(image, scale, interpolation=cv2.INTER_NEAREST):
    w = int(image.shape[1] * scale)
    h = int(image.shape[0] * scale)
    return cv2.resize(image, (w, h), interpolation=interpolation)


def crop(image, bounds):
    x, y, w, h = bounds

    # if x/y are negative adjust w/h and set x/y to zero
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0

    return image[y:y+h,x:x+w]


def crop_ratio(image, bounds):
    ih, iw = image.shape[:2]
    x, y, w, h = bounds
    x = int(x * iw)
    w = int(w * iw)
    y = int(y * ih)
    h = int(h * ih)
    return crop(image, (x, y, w, h))


def threshold(image, value=127, max_value=255, type=cv2.THRESH_BINARY):
    gray = image
    if len(image.shape) == 3:
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, value, max_value, type)
    return cv2.bitwise_and(image, image, mask=mask)
