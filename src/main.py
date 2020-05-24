import sys, os, time, cv2
from helper import clearLayout, getPath, ResultImages
from scaling_pixmap import ScalingPixmapLabel
from video_worker import VideoWorker
from flow_layout import JFlowLayout
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class MainWindow(QMainWindow):
  STATUSBAR_DISPLAY_TIME = 3500
  MAX_CLEANUP_WAIT = 1000
  sig_abort_worker = pyqtSignal()

  def __init__(self):
    super().__init__()
    QThread.currentThread().setPriority(QThread.TimeCriticalPriority)
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

    self.reset_fps_display()
    self.reset_power_display()

    self.vid_worker = None
    self.result_images = None

    self.use_camera()
    
  def stop_video_processor(self):
    self.sig_abort_worker.emit()
    if (self.vid_worker):
      self.vid_worker[1].quit()

  def use_camera(self):
    self.setup_video_worker()
    self.statusbar.showMessage("Using camera feed", self.STATUSBAR_DISPLAY_TIME)
    # TODO: self.show_statusbar_error("Could not get camera feed")

  def open_file(self):
    file_name, _ = QFileDialog.getOpenFileName(self, "Open video", "", "All Files (*);;Movie Files (*.mp4 *.avi)")
    # TODO: Add supported file formats

    if (file_name):
      self.setup_video_worker(file_name)
      self.statusbar.showMessage("Opened file " + file_name, self.STATUSBAR_DISPLAY_TIME)
      # TODO: self.show_statusbar_error("Could not open file")

  def setup_video_worker(self, *args, **kwargs):
    self.stop_video_processor()

    worker = VideoWorker(*args, **kwargs)
    thread = QThread()
    self.vid_worker = (worker, thread)
    worker.moveToThread(thread)

    worker.sig_fps.connect(self.update_fps_display)
    worker.sig_next_frame.connect(self.update_images)
    self.sig_abort_worker.connect(worker.abort)

    thread.started.connect(worker.work)
    thread.start(QThread.IdlePriority) 

  def snapshot(self):
    try:
      path = "./snapshots/" + time.strftime("%d-%m-%Y-%H-%M-%S")
      os.makedirs(path)
      cv2.imwrite(
        os.path.join(path , "input_video.jpg"),
        cv2.cvtColor(self.result_images.current_frame, cv2.COLOR_RGB2BGR)
      )
      cv2.imwrite(
        os.path.join(path , "input_video_annotated.jpg"),
        cv2.cvtColor(self.result_images.current_frame_annotated, cv2.COLOR_RGB2BGR)
      )
      # TODO: save super resolution faces
    except OSError:
      self.show_statusbar_error("Snapshot could not be saved")
    else:
      self.statusbar.showMessage("Snapshot saved in folder: " + path, self.STATUSBAR_DISPLAY_TIME)

  @pyqtSlot(ResultImages)
  def update_images(self, result_images):
    self.result_images = result_images
    current_frame = self.result_images.get_current_frame(self.action_show_annotations.isChecked())
    height, width, channels = current_frame.shape

    if current_frame is not None:
      img = QtGui.QImage(current_frame, width, height, QtGui.QImage.Format_RGB888)
      pix = QtGui.QPixmap.fromImage(img)
      self.video_input.setFullPixmap(pix)

    # TODO
    # clearLayout(self.super_faces_area)
    # for face in self.result_images.super_res_faces:
    #   container = QtWidgets.QWidget()
    #   text_label = QtWidgets.QLabel()
    #   text_label.setText("Face")
    #   image_label = ScalingPixmapLabel(face)
    #   container.setLayout(QtWidgets.QVBoxLayout())
    #   container.layout().addWidget(text_label)
    #   container.layout().addWidget(image_label)
    #   self.super_faces_area.addWidget(container)

  @pyqtSlot(str)
  def update_fps_display(self, fps):
    self.fps_display.setText(fps)

  def reset_fps_display(self):
    self.fps_display.setText("N/A")

  def reset_power_display(self):
    self.power_display.setText("N/A")

  def show_statusbar_error(self, msg):
    self.statusbar.showMessage("ERROR: " + msg, self.STATUSBAR_DISPLAY_TIME)

  def closeEvent(self, event):
    event.accept()
    self.stop_video_processor()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
