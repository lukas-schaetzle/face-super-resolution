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


class ResultImages:
  def __init__(self, frame=None, frame_annotated=None, super_faces=[]):
    self.current_frame = frame
    self.current_frame_annotated = frame_annotated
    self.super_res_faces = super_faces

  def get_current_frame(self, with_annotations=True):
    return self.current_frame_annotated if with_annotations else self.current_frame