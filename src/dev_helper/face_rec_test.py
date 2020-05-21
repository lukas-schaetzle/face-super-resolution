import cv2, face_recognition
from timeit import default_timer as timer

last_timer_value = 0
frame_counter = 0
fps = "N/A"

cap = cv2.VideoCapture(0)

def draw_rect(img, origin, end, descr, color=(18, 156, 243)):
  cv2.rectangle(img, origin, end, color, 2)

  (text_width, text_height), baseline = cv2.getTextSize(descr, cv2.FONT_ITALIC, 0.5, 1)
  text_height += baseline
  cv2.rectangle(img, origin, (origin[0] + text_width, origin[1] + text_height), color, cv2.FILLED)
  cv2.putText(img, descr, (origin[0], origin[1] + text_height - baseline), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)

def calculate_fps():
  global last_timer_value
  global frame_counter
  global fps

  current_time = timer()
  time_since_last_calc = current_time - last_timer_value
  if (time_since_last_calc >= 1.5):
    fps = frame_counter / time_since_last_calc
    last_timer_value = current_time
    frame_counter = 0

def draw_fps(img):
  cv2.putText(img, 'FPS: %.2f'%(fps), (10, 20), cv2.FONT_ITALIC, 0.5, (18, 156, 243), 1)


while(True):
  ret, frame = cap.read()

  face_locations = face_recognition.face_locations(frame)
  for (top, right, bottom, left) in face_locations:
    draw_rect(frame, (left, top), (right, bottom), "test")

  frame_counter += 1
  calculate_fps()
  draw_fps(frame)

  cv2.imshow('frame', frame)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
