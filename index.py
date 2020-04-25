import tkinter, tkinter.filedialog
import cv2
import PIL.Image, PIL.ImageTk
import time

class App:
  def __init__(self, window, window_title, video_source=0):
    self.window = window
    self.window.title(window_title)
    
    menu = tkinter.Menu(self.window)
    self.window.config(menu=menu)

    filemenu = tkinter.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Get Camera Feed", command=self.useCamera)
    filemenu.add_command(label="Open...", command=self.openFile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=self.window.quit)

    helpmenu = tkinter.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About")

    self.vid = MyVideoCapture(video_source)

    self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
    self.canvas.pack()

    self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
    self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

    self.delay = 15
    self.update()

    self.window.mainloop()

  def useCamera(self):
    self.video = MyVideoCapture(0)

  def openFile(self):
    video_source = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    print(video_source)
    self.video = MyVideoCapture(video_source)

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

    self.window.after(self.delay, self.update)


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
