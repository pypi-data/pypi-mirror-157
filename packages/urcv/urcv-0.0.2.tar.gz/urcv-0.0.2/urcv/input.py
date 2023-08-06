import cv2
import random

special_keys = {
    65362: 'up',
    65364: 'down',
    65361: 'left',
    65363: 'right',
    7: 'esc',
    32: 'space',
    13: 'enter',
}

def wait_key(max_time=60000, default=None, delay = 500):
    time = 0
    while time < max_time:
        pressed = cv2.waitKeyEx(delay)
        if pressed in special_keys:
            return special_keys[pressed]
        if pressed != -1:
            return chr(pressed)
        time += delay
    return default


def get_scaled_roi(image, scale):
    w = image.shape[1] * scale
    h = image.shape[0] * scale
    name = f'ROI_{random.random()}'
    bounds = cv2.selectROI(name, cv2.resize(image, (w, h)))
    cv2.destroyWindow(name)
    return [int(i/scale) for i in bounds]
