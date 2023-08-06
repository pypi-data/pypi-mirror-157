import cv2

def write(
  img,
  text,
  font=cv2.FONT_HERSHEY_SIMPLEX,
  pos=(0,0),
  font_scale=1,
  font_thickness=2,
  color=(255, 255, 255),
  bg_color=None,
  align="",
):
  text = str(text)
  x, y = pos
  (text_w, text_h), _ =  cv2.getTextSize(text, font, font_scale, font_thickness)
  if 'bottom' in align:
    y -= text_h
  if 'right' in align:
    x -= text_w

  if bg_color is not None:
    cv2.rectangle(
      img,
      (x, y),
      (x + text_w, y + text_h),
      bg_color,
      -1
    )
  cv2.putText(
    img,
    text,
    (x, int(y + text_h + font_scale - 1)),
    font,
    font_scale,
    color,
    font_thickness
  )

  return (text_w, text_h)