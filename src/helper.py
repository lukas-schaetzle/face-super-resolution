import os

def getPath(*args):
  dirname = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dirname, *args)

def clearLayout(layout):
  # Copied from https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt/13103617

  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
