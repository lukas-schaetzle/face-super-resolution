import sys, os, time, cv2, multiprocessing
from helper import clearLayout, getPath, getNextEvents, ResultImages, SndTopic, RcvTopic, QueueMsg
from scaling_pixmap import ScalingPixmapLabel
from video_worker import VideoProcessInterface
from flow_layout import JFlowLayout
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import pyqtSlot

class MainWindow(QMainWindow):
  STATUSBAR_DISPLAY_TIME = 3500 # in ms
  EVENT_TIMER = 10 # in ms
  MAX_CLEANUP_WAIT = 2 # in s

  def __init__(self):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon(getPath("assets", "icon.png")))
    self.setup_ui()
    
    recv_queue = multiprocessing.Queue()
    send_queue = multiprocessing.Queue()
    self.vid_worker = VideoProcessInterface(send_queue, recv_queue)
    self.vid_worker.process.start()

    self.result_images = None
    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self.handle_incoming_msg)
    self.timer.start(self.EVENT_TIMER)

    # self.use_camera()
  
  def setup_ui(self):
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

  @pyqtSlot()
  def handle_incoming_msg(self):
    messages = getNextEvents(self.vid_worker.recv_queue)
    for msg in messages:
      if (msg.topic == SndTopic.FPS):
        self.update_fps_display(msg.content)
      elif (msg.topic == SndTopic.VIDEO_END):
        pass
      elif (msg.topic == SndTopic.NEXT_FRAME):
        self.update_images(msg.content)
      elif (msg.topic == SndTopic.MSG):
        self.statusbar.showMessage(msg.content, self.STATUSBAR_DISPLAY_TIME)
      elif (msg.topic == SndTopic.MSG_ERROR):
        self.show_statusbar_error(msg.content)
      else:
        print("No endpoint for event topic {topic}".format(topic=msg.topic))

  def use_camera(self):
    self.vid_worker.send_queue.put_nowait(QueueMsg(RcvTopic.USE_CAMERA))

  def open_file(self):
    file_name, _ = QFileDialog.getOpenFileName(self, "Open video", "", "All Files (*);;Movie Files (*.mp4 *.avi)")
    # TODO: Add supported file formats
    if (file_name):
      self.vid_worker.send_queue.put_nowait(QueueMsg(RcvTopic.OPEN_FILE, file_name))

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

  def update_fps_display(self, fps):
    self.fps_display.setText(fps)

  def reset_fps_display(self):
    self.fps_display.setText("N/A")

  def reset_power_display(self):
    self.power_display.setText("N/A")

  def show_statusbar_error(self, msg):
    self.statusbar.showMessage("ERROR: " + msg, self.STATUSBAR_DISPLAY_TIME)

  def handle_video_end(self):
    self.statusbar.showMessage("Video feed ended", self.STATUSBAR_DISPLAY_TIME)
    self.reset_fps_display

  def closeEvent(self, event):
    event.accept()
    self.vid_worker.send_queue.put_nowait(QueueMsg(RcvTopic.KILL))
    self.vid_worker.process.join()
    if (self.vid_worker.process.is_alive()):
      self.vid_worker.process.terminate()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())
