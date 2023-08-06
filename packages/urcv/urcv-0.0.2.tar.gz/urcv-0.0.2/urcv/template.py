import cv2
from imutils.object_detection import non_max_suppression
import numpy as np

def match(image, template, threshold=0.9, mask=None):
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED, mask=mask)

    (yCoords, xCoords) = np.where(result >= threshold)
    (tH, tW) = template.shape[:2]

    coords = [(x, y, x + tW, y + tH) for (x, y) in zip(xCoords, yCoords)]
    pick = non_max_suppression(np.array(coords))
    return pick


def union(image, template):
    """
    Extract only the pixels that match the template.
    """
    diff = cv2.absdiff(image, template)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    imask = mask == 0

    canvas = np.zeros_like(image, np.uint8)
    canvas[imask] = image[imask]
    return canvas