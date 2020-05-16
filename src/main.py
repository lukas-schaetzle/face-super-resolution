import sys, os, time, cv2
from helper import clearLayout, getPath
from scaling_pixmap import ScalingPixmapLabel
from video_interface import VideoInterface
from flow_layout import JFlowLayout
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

class MainWindow(QMainWindow):
  STATUSBAR_DISPLAY_TIME = 3500
  MAX_CLEANUP_WAIT = 1000

  def __init__(self):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon(getPath("assets", "icon.png")))

    uic.loadUi(getPath("assets", "main.ui"), self)
    self.layout_video_input = self.findChild(QtWidgets.QVBoxLayout, 'layout_videoInput')
    self.statusbar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
    super_faces_area_widget = self.findChild(QtWidgets.QWidget, 'scrollAreaWidgetContents')
    self.action_snapshot = self.findChild(QtWidgets.QAction, 'actionSnapshot')
    self.action_close = self.findChild(QtWidgets.QAction, 'actionClose')
    self.action_use_camera = self.findChild(QtWidgets.QAction, 'actionGet_camera_feed')
    self.action_open_file = self.findChild(QtWidgets.QAction, 'actionOpen_video_file')
    self.action_show_annotations = self.findChild(QtWidgets.QAction, 'actionShow_annotations')
    self.fps_display = self.findChild(QtWidgets.QLineEdit, 'FPSLineEdit')
    self.power_display = self.findChild(QtWidgets.QLineEdit, 'PowerLineEdit')

    self.video_input = ScalingPixmapLabel()
    self.layout_video_input.addWidget(self.video_input)

    self.super_faces_area = JFlowLayout()
    super_faces_area_widget.setLayout(self.super_faces_area)

    self.action_close.triggered.connect(self.close)
    self.action_snapshot.triggered.connect(self.snapshot)
    self.action_use_camera.triggered.connect(self.use_camera)
    self.action_open_file.triggered.connect(self.open_file)

    self.vid = None
    self.use_camera()
    
  def stop_video_processor(self):
    if (self.vid):
      self.vid.stop()

  def use_camera(self):
    self.stop_video_processor()

    self.vid = VideoInterface(self, 0)
    self.vid.start()

    try:
      
      self.statusbar.showMessage("Using camera feed", self.STATUSBAR_DISPLAY_TIME)
    except:
      self.show_statusbar_error("Could not get camera feed")

  def open_file(self):
    self.stop_video_processor()

    file_name, _ = QFileDialog.getOpenFileName(self, "Open video", "", "All Files (*);;Movie Files (*.mp4 *.avi)")
    # TODO: Add supported file formats

    if (file_name):
      try:
        self.vid = VideoInterface(self, file_name)
        self.vid.start()
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
    current_frame = self.vid.get_current_frame(self.action_show_annotations.isChecked())

    if current_frame is not None:
      img = QtGui.QImage(current_frame, self.vid.width, self.vid.height, QtGui.QImage.Format_RGB888)
      pix = QtGui.QPixmap.fromImage(img)
      self.video_input.setFullPixmap(pix)

    self.fps_display.setText('%.2f'%(self.vid.fps) if self.vid.fps else "N/A")
    self.power_display.setText("N/A")

    clearLayout(self.super_faces_area)
    for face in self.vid.super_res_faces:
      container = QtWidgets.QWidget()
      text_label = QtWidgets.QLabel()
      text_label.setText("Face")
      image_label = ScalingPixmapLabel(face)
      container.setLayout(QtWidgets.QVBoxLayout())
      container.layout().addWidget(text_label)
      container.layout().addWidget(image_label)
      self.super_faces_area.addWidget(container)

  def show_statusbar_error(self, msg):
    self.statusbar.showMessage("ERROR: " + msg, self.STATUSBAR_DISPLAY_TIME)

  def closeEvent(self, event):
    event.accept()
    if (self.vid):
      self.vid.stop()
      if (not self.vid.wait(self.MAX_CLEANUP_WAIT)):
        self.vid.terminate()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
