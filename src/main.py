import sys, os, time
import cv2
from scaling_pixmap import ScalingPixmapLabel
from video_capture import MyVideoCapture
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
  STATUSBAR_DISPLAY_TIME = 3500

  def __init__(self):
    super().__init__()

    uic.loadUi('main.ui', self)
    self.layout_video_input = self.findChild(QtWidgets.QVBoxLayout, 'layout_videoInput')
    self.statusbar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
    self.action_snapshot = self.findChild(QtWidgets.QAction, 'actionSnapshot')
    self.action_close = self.findChild(QtWidgets.QAction, 'actionClose')
    self.action_use_camera = self.findChild(QtWidgets.QAction, 'actionGet_camera_feed')
    self.action_open_file = self.findChild(QtWidgets.QAction, 'actionOpen_video_file')
    self.action_show_annotations = self.findChild(QtWidgets.QAction, 'actionShow_annotations')

    self.video_input = ScalingPixmapLabel()
    self.layout_video_input.addWidget(self.video_input)

    self.action_close.triggered.connect(self.close)
    self.action_snapshot.triggered.connect(self.snapshot)
    self.action_use_camera.triggered.connect(self.use_camera)
    self.action_open_file.triggered.connect(self.open_file)

    self.vid = MyVideoCapture(0)
    self.timer = QtCore.QTimer()
    #self.timer.setSingleShot(True)
    self.timer.timeout.connect(self.update)
    self.timer.start(20)

  def use_camera(self):
    try:
      self.vid = MyVideoCapture(0)
      self.statusbar.showMessage("Using camera feed", self.STATUSBAR_DISPLAY_TIME)
    except:
      self.show_statusbar_error("Could not get camera feed")

  def open_file(self):
    file_name, _ = QFileDialog.getOpenFileName(self, "Open video", "", "All Files (*);;Movie Files (*.mp4 *.avi)")

    if (file_name):
      try:
        self.vid = MyVideoCapture(file_name)
        self.statusbar.showMessage("Opened file " + file_name, self.STATUSBAR_DISPLAY_TIME)
      except:
        self.show_statusbar_error("Could not open file")

  def snapshot(self):
    try:
      path = "./snapshots/" + time.strftime("%d-%m-%Y-%H-%M-%S")
      os.makedirs(path)
      cv2.imwrite(
        os.path.join(path , "input_video.jpg"),
        cv2.cvtColor(self.vid.current_frame, cv2.COLOR_RGB2BGR)
      )
      cv2.imwrite(
        os.path.join(path , "input_video_annotated.jpg"),
        cv2.cvtColor(self.vid.current_frame_annotated, cv2.COLOR_RGB2BGR)
      )
    except OSError:
      self.show_statusbar_error("Snapshot could not be saved")
    else:
      self.statusbar.showMessage("Snapshot saved in folder: " + path, self.STATUSBAR_DISPLAY_TIME)

  def update(self):
    self.vid.next_frame()
    current_frame = self.vid.get_current_frame(self.action_show_annotations.isChecked())

    if current_frame is not None:
      img = QtGui.QImage(current_frame, self.vid.width, self.vid.height, QtGui.QImage.Format_RGB888)
      pix = QtGui.QPixmap.fromImage(img)
      self.video_input.setFullPixmap(pix)

  def show_statusbar_error(self, msg):
    self.statusbar.showMessage("ERROR: " + msg, self.STATUSBAR_DISPLAY_TIME)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
