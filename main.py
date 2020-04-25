import time
import tkinter, tkinter.filedialog, tkinter.ttk
import cv2
import PIL.Image, PIL.ImageTk

class App:
  def __init__(self, root, window_title, video_source=0):
    self.root = root
    self.root.option_add('*tearOff', tkinter.FALSE)
    self.root.title(window_title)
    
    self._addMenuBar(self.root)
    frame = tkinter.ttk.Frame(self.root)
    frame.pack(pady=5, padx=5)

    self.vid = MyVideoCapture(video_source)
    self.canvas = tkinter.Canvas(frame, width = self.vid.width, height = self.vid.height)
    self.canvas.pack()

    self.btn_snapshot=tkinter.Button(frame, text="Take snapshot", command=self.snapshot)
    self.btn_snapshot.pack(anchor=tkinter.W, pady=(5, 0))

    self.delay = 15
    self.update()

    self.root.mainloop()

  def _addMenuBar(self, window):
    menu = tkinter.Menu(window)
    window.config(menu=menu)

    filemenu = tkinter.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Get camera feed", command=self.useCamera)
    filemenu.add_command(label="Open movie file...", command=self.openFile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=window.quit)

    helpmenu = tkinter.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About")

  def useCamera(self):
    self.vid = MyVideoCapture(0)

  def openFile(self):
    video_source = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("movie files","*.avi"),("all files","*.*")))
    self.vid = MyVideoCapture(video_source)

  # Get a frame from the video source
  def snapshot(self):
    ret, frame = self.vid.get_frame()
    if ret:
      cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

  def update(self):
    ret, frame = self.vid.get_frame()

    if ret:
      self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
      self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW) 

    self.root.after(self.delay, self.update)


class MyVideoCapture:
  def __init__(self, video_source=0):
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
 
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()

  def get_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      if ret:
        return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
      else:
        return (ret, None)
    else:
      return (ret, None)


App(tkinter.Tk(), "First Test")
