from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

class FaceSetContainer(QtWidgets.QWidget):
  def __init__(self, title, pixmaps, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.size = QtCore.QSize(128, 128)

    self.label = QtWidgets.QLabel()
    self.label.setText(title)

    img_container = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout()
    layout.setAlignment(Qt.AlignLeft)
    layout.setContentsMargins(0,0,0,0)
    img_container.setLayout(layout)

    self.pixmaps = []
    for pixmap in pixmaps:
      widget = QtWidgets.QLabel()
      widget.setPixmap(pixmap.scaled(
        self.size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
      ))
      self.pixmaps.append(widget)
      img_container.layout().addWidget(widget)

    wrapper_layout = QtWidgets.QVBoxLayout()
    wrapper_layout.addWidget(self.label)
    wrapper_layout.addWidget(img_container)
    wrapper_layout.setAlignment(Qt.AlignTop)
    self.setLayout(wrapper_layout)


  def replace(self, pixmaps, title=None):
    if title:
      self.label.setText(title)
    
    for index, pixmap in enumerate(pixmaps, 0):
      self.pixmaps[index].setPixmap(pixmap.scaled(
        self.size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
      ))
    