import os, platform, cv2
from enum import Enum
from queue import Empty as EmptyError
from PyQt5 import QtGui

def transformToPixmap(cv_img):
  height, width, channel = cv_img.shape
  bytesPerLine = 3 * width
  q_img = QtGui.QImage(cv_img.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
  return QtGui.QPixmap(q_img)

def upscaleTuple(scale_factor, tuple_inp):
  return tuple(int(round(scale_factor * x)) for x in tuple_inp)

def resizeImage(cv_img, max_width, max_height):
  height, width = cv_img.shape[:2]

  h_ratio = max_height / height
  w_ratio = max_width / width
  scale_factor = min(h_ratio, w_ratio)
  return cv2.resize(cv_img, (0,0), fx=scale_factor, fy=scale_factor), scale_factor

def getPath(current_working_dir, *args):
  dirname = os.path.dirname(os.path.realpath(current_working_dir))
  return os.path.join(dirname, *args)

def clearLayout(layout):
  # Copied from https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt/13103617

  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()

def getNextEvents(queue, max_event_num=10):
  res = []

  for i in range(max_event_num):
    try:
      msg = queue.get_nowait()
      res.append(msg)
    except EmptyError:
      break

  return res

def running_on_jetson_nano():
  return platform.machine() == "aarch64"

class SndTopic(Enum):
  # Sent by subprocess
  FPS = 1
  VIDEO_END = 2
  NEXT_FRAME = 3
  MSG = 4
  MSG_ERROR = 5

class RcvTopic(Enum):
  # Received by subprocess
  KILL = 1
  USE_CAMERA = 2
  OPEN_FILE = 3
  END_VID = 4

class ResultImages:
  def __init__(self, frame=None, frame_annotated=None, super_faces=[]):
    self.current_frame = frame
    self.current_frame_annotated = frame_annotated
    self.super_res_faces = super_faces

  def get_current_frame(self, with_annotations=True):
    return self.current_frame_annotated if with_annotations else self.current_frame

class QueueMsg():
  def __init__(self, topic, content=None):
    self.topic = topic
    self.content = content

# class FaceArea():
#   def __init__(self, face, max_dimensions):
#     max_width = max_dimensions[0]
#     max_height = max_dimensions[1]
    
#     side_len = max(face.Width, face.Height)
#     side_half_len = round(side_len / 2)

#     self.left = max(0, face.Center[0] - side_half_len)
#     self.top = max(0, face.Center[1] - side_half_len)
#     self.right = min(max_width - 1, face.Center[2] + side_half_len)
#     self.bottom = min(max_height + 1, face.Center[2] + side_half_len)
  
#   def is_square(self):
#     return (self.right - self.left == self.bottom - self.top)

class FaceArea():
  def __init__(self, left, top, right, bottom):
    self.left = left
    self.top = top
    self.right = right
    self.bottom = bottom

def downscale_to_16x16(img):
  img_64, _ = resizeImage(img, 64, 64)
  img_32, _ = resizeImage(img_64, 32, 32)
  img_16, _ = resizeImage(img_32, 16, 16)
  return img_16
