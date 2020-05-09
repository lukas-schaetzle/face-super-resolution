from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

class ScalingPixmapLabel(QtWidgets.QLabel):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setMinimumSize(1, 1)
    self.setAlignment(Qt.AlignCenter)
    self.original_pixmap = None

  def resizeEvent(self, evt):
    if self.original_pixmap:
      self.setScaledPixmap()

  def setFullPixmap(self, full_pixmap):
    self.original_pixmap = full_pixmap
    self.setScaledPixmap()

  def setScaledPixmap(self):
    size = self.size()
    height = min(size.height(), self.original_pixmap.height())
    width = min(size.width(), self.original_pixmap.width())
    size = QtCore.QSize(width, height)

    self.setPixmap(self.original_pixmap.scaled(size,
      Qt.KeepAspectRatio,
      Qt.SmoothTransformation
    ))

