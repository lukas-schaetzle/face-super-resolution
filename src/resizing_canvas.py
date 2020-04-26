import tkinter as tk

class ResizingCanvas(tk.Canvas):
  def __init__(self, parent, **kwargs):
    tk.Canvas.__init__(self, parent, **kwargs)
    self.bind("<Configure>", self.on_resize)
                   
  def on_resize(self, event):
    width = self.winfo_width()
    height = self.winfo_height()
    x0, y0, x1, y1 = self.bbox('all')
    xratio = float(width) / x1
    yratio = float(height) / y1
    
    if xratio < yratio:
      self.scale_objects(xratio)
    else:
      self.scale_objects(yratio)

  def scale_objects(self, scale):
    self.scale('all', 0, 0, scale, scale)
