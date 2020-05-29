#!/usr/bin/env python3

import sys, os, time, cv2, multiprocessing
from modules.custom_qt import FaceSetContainer, JFlowLayout, ScalingPixmapLabel
from modules.helper import *
from power_usage import get_power_usage
from video_worker import VideoProcessInterface
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog
from PyQt5.QtCore import pyqtSlot, Qt

class MainWindow(QMainWindow):
  STATUSBAR_DISPLAY_TIME = 3500 # in ms
  EVENT_TIMER = 10 # in ms
  POWER_USAGE_TIMER = 1000 # in ms
  MAX_CLEANUP_WAIT = 2 # in s
  DISPLAY_NA = "N/A"

  def __init__(self):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon(getPath(__file__, "assets", "icon.png")))
    self.setup_ui()

    recv_queue = multiprocessing.Queue()
    send_queue = multiprocessing.Queue()
    self.vid_worker = VideoProcessInterface(send_queue, recv_queue)
    self.vid_worker.process.start()

    self.result_images = None

    self.evt_timer = QtCore.QTimer()
    self.evt_timer.timeout.connect(self.handle_incoming_msg)
    self.evt_timer.start(self.EVENT_TIMER)

    if running_on_jetson_nano():
      self.power_usg_timer = QtCore.QTimer()
      self.power_usg_timer.timeout.connect(self.update_power_display)
      self.power_usg_timer.start(self.POWER_USAGE_TIMER)

  def setup_ui(self):
    uic.loadUi(getPath(__file__, "assets/main.ui"), self)
    self.layout_video_input = self.findChild(QtWidgets.QVBoxLayout, 'layout_videoInput')
    self.statusbar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
    super_faces_area_widget = self.findChild(QtWidgets.QWidget, 'scrollAreaWidgetContents')
    self.action_snapshot = self.findChild(QtWidgets.QAction, 'actionSnapshot')
    self.action_close = self.findChild(QtWidgets.QAction, 'actionClose')
    self.action_use_camera = self.findChild(QtWidgets.QAction, 'actionGet_camera_feed')
    self.action_open_file = self.findChild(QtWidgets.QAction, 'actionOpen_video_file')
    self.action_show_annotations = self.findChild(QtWidgets.QAction, 'actionShow_annotations')
    self.action_about = self.findChild(QtWidgets.QAction, 'actionAbout')
    self.fps_display = self.findChild(QtWidgets.QLineEdit, 'FPSLineEdit')
    self.psnr_display = self.findChild(QtWidgets.QLineEdit, 'PSNRLineEdit')
    self.power_display = self.findChild(QtWidgets.QLineEdit, 'PowerLineEdit')

    self.video_input = ScalingPixmapLabel()
    self.layout_video_input.addWidget(self.video_input)

    self.super_faces_area = QtWidgets.QVBoxLayout()
    self.super_faces_area.setAlignment(Qt.AlignTop)
    super_faces_area_widget.setLayout(self.super_faces_area)
    self.face_sets = []

    self.action_close.triggered.connect(self.close)
    self.action_snapshot.triggered.connect(self.snapshot)
    self.action_use_camera.triggered.connect(self.use_camera)
    self.action_open_file.triggered.connect(self.open_file)
    self.action_about.triggered.connect(self.showAboutDialog)

    self.reset_fps_display()
    self.reset_psnr_display()
    self.reset_power_display()

  @pyqtSlot()
  def handle_incoming_msg(self):
    messages = getNextEvents(self.vid_worker.recv_queue)
    for msg in messages:
      if (msg.topic == SndTopic.FPS):
        self.update_fps_display(msg.content)
      elif (msg.topic == SndTopic.PSNR):
        self.update_psnr_display(msg.content)
      elif (msg.topic == SndTopic.VIDEO_END):
        self.handle_video_end()
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
      parent_path = os.path.join("./snapshots/" + time.strftime("%d-%m-%Y-%H-%M-%S"))
      os.makedirs(parent_path)
      cv2.imwrite(
        os.path.join(parent_path , "input_video.jpg"),
        cv2.cvtColor(self.result_images.current_frame, cv2.COLOR_RGB2BGR)
      )
      cv2.imwrite(
        os.path.join(parent_path , "input_video_annotated.jpg"),
        cv2.cvtColor(self.result_images.current_frame_annotated, cv2.COLOR_RGB2BGR)
      )

      psnr_file = open(os.path.join(parent_path , "psnr.csv"), "w")

      for index, face_set in enumerate(self.result_images.super_res_faces, 1):
        psnr_file.write(f"Face {index},{face_set.psnr} dB\n")
        path = os.path.join(parent_path , f"face_{index}")
        os.makedirs(path)
        for index, face in enumerate(face_set.faces):
          cv2.imwrite(
            os.path.join(path , face[0] + ".jpg"),
            cv2.cvtColor(face[1], cv2.COLOR_RGB2BGR)
          )

      psnr_file.close()

    except OSError:
      self.show_statusbar_error("Snapshot could not be saved")
    else:
      self.statusbar.showMessage("Snapshot saved in folder: " + parent_path, self.STATUSBAR_DISPLAY_TIME)

  def update_images(self, result_images):
    self.result_images = result_images
    current_frame = self.result_images.get_current_frame(self.action_show_annotations.isChecked())
    height, width, channels = current_frame.shape

    if current_frame is not None:
      img = QtGui.QImage(current_frame, width, height, QtGui.QImage.Format_RGB888)
      pix = QtGui.QPixmap.fromImage(img)
      self.video_input.setFullPixmap(pix)

    for index, face_set in enumerate(self.result_images.super_res_faces, 0):
      current_number = index + 1
      image_set = map(lambda x: transformToPixmap(x[1]), face_set.faces)

      if len(self.face_sets) >= current_number:
        self.face_sets[index].replace(image_set)
      else:
        container = FaceSetContainer(f"Face {current_number}:", image_set)
        self.face_sets.append(container)
        self.super_faces_area.addWidget(container)

    target_number = len(self.result_images.super_res_faces)
    current_number = len(self.face_sets)
    if current_number > target_number:
      for index in range(current_number-1, target_number-1, -1):
        child = self.super_faces_area.takeAt(index)
        if child and child.widget():
          child.widget().deleteLater()
        self.face_sets.pop()

  def update_fps_display(self, fps):
    self.fps_display.setText(fps)

  def update_psnr_display(self, psnr):
    self.psnr_display.setText(psnr)

  @pyqtSlot()
  def update_power_display(self):
    self.power_display.setText(get_power_usage())

  def reset_fps_display(self):
    self.fps_display.setText(self.DISPLAY_NA)

  def reset_psnr_display(self):
    self.psnr_display.setText(self.DISPLAY_NA)

  def reset_power_display(self):
    self.power_display.setText(self.DISPLAY_NA)

  def show_statusbar_error(self, msg):
    self.statusbar.showMessage("ERROR: " + msg, self.STATUSBAR_DISPLAY_TIME)

  def handle_video_end(self):
    self.statusbar.showMessage("Video feed ended", self.STATUSBAR_DISPLAY_TIME)
    self.reset_fps_display()
    self.reset_psnr_display()

  def closeEvent(self, event):
    event.accept()
    self.vid_worker.send_queue.put_nowait(QueueMsg(RcvTopic.KILL))
    self.vid_worker.process.join()
    if (self.vid_worker.process.is_alive()):
      self.vid_worker.process.terminate()

  def showAboutDialog(self):
    AboutDialog().exec_()

class AboutDialog(QDialog):
  def __init__(self):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon(getPath(__file__, "assets", "icon.png")))
    uic.loadUi(getPath(__file__, "assets/about.ui"), self)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())
