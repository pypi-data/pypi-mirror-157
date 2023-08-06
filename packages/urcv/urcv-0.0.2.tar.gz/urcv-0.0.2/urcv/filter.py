import cv2


def brightness(image, value=30):
    has_alpha = image.shape[-1] == 4
    if has_alpha:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGRA2HSVA)
        h, s, v, a = cv2.split(hsv)
    else:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
    v = cv2.add(v,value)
    v[v > 255] = 255
    v[v < 0] = 0
    if has_alpha:
        final_hsv = cv2.merge((h, s, v, a))
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSVA2BGRA)
    else:
        final_hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)


adjust_brightness = brightness

def chain(image, brightness=0, multiply=None):
    if brightness:
        image = adjust_brightness(image, brightness)
    if multiply is not None:
        image = cv2.multiply(image, multiply)
    return image
