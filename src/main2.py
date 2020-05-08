import sys, os, time
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
  STATUSBAR_DISPLAY_TIME = 3500

  def __init__(self):
    super().__init__()

    uic.loadUi('main.ui', self)

    self.video_input = self.findChild(QtWidgets.QLabel, 'videoInput')
    self.statusbar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
    self.action_snapshot = self.findChild(QtWidgets.QAction, 'actionSnapshot')
    self.action_close = self.findChild(QtWidgets.QAction, 'actionClose')

    self.addStatusbarWidgets()

    self.action_close.triggered.connect(self.close)
    self.action_snapshot.triggered.connect(self.snapshot)
    

  def addStatusbarWidgets(self):
    self.label_fps = QtWidgets.QLabel("FPS: N/A")
    self.label_power_usage = QtWidgets.QLabel("Power usage: N/A")
    self.statusbar.addPermanentWidget(self.label_fps, 0.1)
    self.statusbar.addPermanentWidget(self.label_power_usage, 0.1)
  

  def snapshot(self):
    try:
      path = "./snapshots/" + time.strftime("%d-%m-%Y-%H-%M-%S")
      os.makedirs(path)
    except OSError:
      self.statusbar.showMessage("ERROR: Snapshot could not be saved", self.STATUSBAR_DISPLAY_TIME)
    else:
      self.statusbar.showMessage("Snapshot saved in folder: " + path, self.STATUSBAR_DISPLAY_TIME)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
