import os, platform, cv2, numpy, # torchvision.transforms as transforms
from enum import Enum
from queue import Empty as EmptyError
from PyQt5 import QtGui
from PIL import Image

def transformToPixmap(cv_img):
  height, width, channel = cv_img.shape
  bytesPerLine = 3 * width
  q_img = QtGui.QImage(cv_img.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
  return QtGui.QPixmap(q_img)

def upscaleTuple(scale_factor, tuple_inp):
  return tuple(int(round(scale_factor * x)) for x in tuple_inp)

def resizeImage(cv_img, max_width, max_height, interpolation=cv2.INTER_LINEAR):
  height, width = cv_img.shape[:2]

  h_ratio = max_height / height
  w_ratio = max_width / width
  scale_factor = min(h_ratio, w_ratio)
  return cv2.resize(cv_img, (0,0), fx=scale_factor, fy=scale_factor, interpolation=interpolation), scale_factor

def getPath(current_working_dir, *args):
  dirname = os.path.dirname(os.path.realpath(current_working_dir))
  return os.path.join(dirname, *args)

def clearLayout(layout):
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
  PSNR = 6

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

class FaceArea():
  def __init__(self, corners=None, center_w_h=None, max_dim=None):
    width = height = 0

    if corners is not None:
      left, top, right, bottom = corners
      width = right - left
      height = bottom - top
      self.center = (width / 2 + left, height / 2 + top)
    else:
      self.center, width, height = center_w_h

    side_len = max(width, height)
    side_half_len = side_len / 2

    self.left = int(round(   max(0, self.center[0] - side_half_len) ))
    self.top = int(round(    max(0, self.center[1] - side_half_len) ))

    if max_dim:
      max_width, max_height = max_dim
      self.right = int(round(  min(max_width, self.center[0] + side_half_len) ))
      self.bottom = int(round( min(max_height, self.center[1] + side_half_len) ))
    else:
      self.right = int(round(  self.center[0] + side_half_len ))
      self.bottom = int(round( self.center[1] + side_half_len ))
    
  def is_square(self):
    return (self.right - self.left == self.bottom - self.top)

class SuperResFaceResult():
  def __init__(self, target_face, input_face, output_face, psnr):
    self.faces = (
      ("target", target_face),
      ("low_res", input_face),
      ("super_res", output_face),
    )
    self.psnr = psnr

def downscale_to_16x16(img):
  _64x64_down_sampling = transforms.Resize((64, 64))
  _32x32_down_sampling = transforms.Resize((32, 32))
  _16x16_down_sampling = transforms.Resize((16, 16))

  pil_img = Image.fromarray(img)
  downsized_pil_img = _16x16_down_sampling(_32x32_down_sampling(_64x64_down_sampling(pil_img)))
  return numpy.array(downsized_pil_img)
