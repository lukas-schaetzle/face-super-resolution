import threading, time, cv2, face_recognition
from PyQt5 import QtGui, QtCore
from helper import getPath
from timeit import default_timer as timer

# TODO: cleanup with own thread objects

class VideoInterface(QtCore.QThread):
  video_frames_ready = QtCore.pyqtSignal() 

  def __init__(self, parent=None, video_source=0, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self._stop_event = threading.Event()

    self._frame_counter = 0
    self._last_timer_value = None
    self.fps = None

    self.video_frames_ready.connect(parent.update)

    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
 
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.current_frame = None
    self.current_frame_annotated = None
    self.super_res_faces = [QtGui.QPixmap(getPath("assets", "test.png")) for x in range(4)]

  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()

  def run(self):
    self._last_timer_value = timer()
    while (not self._stop_event.is_set()):
      self.next_frame()
      self.calculate_fps()
      # TODO: stop when video file finished
    print("Thread stopped properly") # TODO: remove debug msg
    
  def stop(self):
    self._stop_event.set()

  def calculate_fps(self):
    current_time = timer()
    time_since_last_calc = current_time - self._last_timer_value
    if (time_since_last_calc >= 1.5):
      self.fps = self._frame_counter / time_since_last_calc
      self._last_timer_value = current_time
      self._frame_counter = 0
    
  def next_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      
      if ret:
        annotatedFrame = frame.copy()
        self.draw_rect(annotatedFrame, (20, 20), (100, 100), "1")
        
        time.sleep(1)
        # face_locations = face_recognition.face_locations(annotatedFrame)
        # for (top, right, bottom, left) in face_locations:
        #   self.draw_rect(annotatedFrame, (left, top), (right, bottom), "test")

        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.current_frame_annotated = cv2.cvtColor(annotatedFrame, cv2.COLOR_BGR2RGB)
        self._frame_counter += 1
        self.video_frames_ready.emit()

  def get_current_frame(self, with_annotations=True):
    return self.current_frame_annotated if with_annotations else self.current_frame

  def draw_rect(self, img, origin, end, descr, color=(18, 156, 243)):
    cv2.rectangle(img, origin, end, color, 2)

    (text_width, text_height), baseline = cv2.getTextSize(descr, cv2.FONT_ITALIC, 0.5, 1)
    text_height += baseline
    cv2.rectangle(img, origin, (origin[0] + text_width, origin[1] + text_height), color, cv2.FILLED)
    cv2.putText(img, descr, (origin[0], origin[1] + text_height - baseline), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
