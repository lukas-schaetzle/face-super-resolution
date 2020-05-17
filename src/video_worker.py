#!/usr/bin/env python3

import threading, time, cv2, face_recognition
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from helper import getPath, ResultImages
from timeit import default_timer as timer
from test import Test

class VideoWorker(QObject):
  sig_fps = pyqtSignal(str) 
  sig_next_frame = pyqtSignal(ResultImages)

  def __init__(self, video_source=0, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._abort = False

    self._frame_counter = 0
    self._last_timer_value = None
    self.fps = None

    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
 
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.current_frame = None
    self.current_frame_annotated = None
    self.super_res_faces = [QtGui.QPixmap(getPath("assets", "test.png")) for x in range(4)]

  @pyqtSlot()
  def work(self):
    # self.t = []
    # for x in range(20):
    #   self.t.append(Test())
    #   self.t[-1].start()

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
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      
      if ret:
        annotatedFrame = frame.copy()
        # self.draw_rect(annotatedFrame, (20, 20), (100, 100), "1")

        # for x in range(59999999):
        #   z = 1 + 1

        face_locations = face_recognition.face_locations(annotatedFrame)
        for (top, right, bottom, left) in face_locations:
          self.draw_rect(annotatedFrame, (left, top), (right, bottom), "test")

        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.current_frame_annotated = cv2.cvtColor(annotatedFrame, cv2.COLOR_BGR2RGB)
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
