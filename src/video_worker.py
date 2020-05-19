import threading, time, cv2, jetson.inference, jetson.utils
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from helper import getPath, ResultImages
from timeit import default_timer as timer
import numpy as np

class VideoWorker(QObject):
  sig_fps = pyqtSignal(str) 
  sig_next_frame = pyqtSignal(ResultImages)

  def __init__(self, video_source=0, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._abort = False

    self._frame_counter = 0
    self._last_timer_value = None
    self.fps = None

    self.vid = None
 
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.current_frame = None
    self.current_frame_annotated = None
    self.super_res_faces = [QtGui.QPixmap(getPath("assets", "test.png")) for x in range(4)]

    self.net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
    self.cam = jetson.utils.gstCamera(640, 360, "/dev/video0")

  @pyqtSlot()
  def work(self):
    self._last_timer_value = timer()
    while (not self._abort):
      # TODO: stop when video file finished
      self.next_frame()
      self.calculate_fps()

      QtCore.QCoreApplication.processEvents()

    print("Thread stopped properly") # TODO: remove debug msg

  def calculate_fps(self):
    current_time = timer()
    time_since_last_calc = current_time - self._last_timer_value
    if (time_since_last_calc >= 1.5):
      self.fps = self._frame_counter / time_since_last_calc
      self._last_timer_value = current_time
      self._frame_counter = 0

      if (not self._abort):
        self.sig_fps.emit('%.2f'%(self.fps))

  def next_frame(self):
    img, width, height = self.cam.CaptureRGBA()
    face_locations = self.net.Detect(img, width, height)

    for face in face_locations:
      print(face_locations)
    
    img = jetson.utils.cudaToNumpy(img, width, height, 4)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB).astype(np.uint8)
    self.current_frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    self.current_frame_annotated = self.current_frame
    self._frame_counter += 1

    if (not self._abort):
      self.sig_next_frame.emit(ResultImages(self.current_frame, self.current_frame_annotated, self.super_res_faces))
    
  def draw_rect(self, img, origin, end, descr, color=(18, 156, 243)):
    cv2.rectangle(img, origin, end, color, 2)

    (text_width, text_height), baseline = cv2.getTextSize(descr, cv2.FONT_ITALIC, 0.5, 1)
    text_height += baseline
    cv2.rectangle(img, origin, (origin[0] + text_width, origin[1] + text_height), color, cv2.FILLED)
    cv2.putText(img, descr, (origin[0], origin[1] + text_height - baseline), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)

  @pyqtSlot()
  def abort(self):
    self._abort = True
