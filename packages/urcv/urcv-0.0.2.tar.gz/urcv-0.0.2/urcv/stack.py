import cv2
import numpy as np


def many(images, text=None, border=False, text_color=(255,255,255)):
    w = int(np.ceil(len(images)**0.5))
    h = int(np.ceil(len(images)/w))
    if h < 2:
        return np.hstack(images)

    (ih, iw, ic) = images[0].shape
    result = np.zeros((h*ih, w*iw, ic), dtype=np.uint8)
    for index, image in enumerate(images):
        x0 = iw * (index % w)
        y0 = ih * int(np.floor(index / w))
        result[y0:y0+ih,x0:x0+iw,:] = image
    for index, image in enumerate(images):
        x0 = iw * (index % w)
        y0 = ih * int(np.floor(index / w))
        if text:
            cv2.putText(result, text[index], (x0+5, y0+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color)
        if border:
            cv2.line(result, (x0+iw, y0), (x0+iw, y0+ih), border, 1)
            cv2.line(result, (x0, y0+ih), (x0+iw, y0+ih), border, 1)
    return result

def many_grays(images, **kwargs):
    converted = []
    for image in images:
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        converted.append(image)
    return many(converted, **kwargs)