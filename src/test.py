from PyQt5.QtCore import QThread

class Test(QThread):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def run(self):
    while True:
      z = 1+1
