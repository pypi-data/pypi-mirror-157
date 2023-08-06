import cv2
from collections import OrderedDict
import numpy as np


def filter(hsv, hue=[0,180], saturation=[0, 255], value=[0, 255]):
    lower = np.array([hue[0], saturation[0], value[0]])
    upper = np.array([hue[1], saturation[1], value[1]])
    mask = cv2.inRange(hsv, lower, upper)
    return cv2.bitwise_and(hsv, hsv, mask=mask)


def scan_hue(hsv, n_steps=12, **kwargs):
    s = 180 / n_steps
    ranges = [(int(i*s), int((i+1) * s)) for i in range(n_steps)]
    results = [filter(hsv, hue=r, **kwargs) for r in ranges]
    return results, ranges


def hist(hsv):
    h_bins = 50
    s_bins = 60
    histSize = [h_bins, s_bins]
    # hue varies from 0 to 179, saturation from 0 to 255
    h_ranges = [0, 180]
    s_ranges = [0, 256]
    ranges = h_ranges + s_ranges # concat lists
    # Use the 0-th and 1-st channels
    channels = [0, 1]
    return cv2.calcHist([hsv], channels, None, histSize, ranges, accumulate=False)