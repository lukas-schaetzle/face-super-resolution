import time
import tkinter as tk, tkinter.filedialog, tkinter.ttk
import cv2
import PIL.Image, PIL.ImageTk

from resizing_canvas import ResizingCanvas
from video_capture import MyVideoCapture

class App:
  def __init__(self, root, window_title, video_source=0):
    self.root = root
    self.root.option_add('*tearOff', tk.FALSE)
    self.root.title(window_title)

    self.vid = MyVideoCapture(video_source)

    self._addMenuBar(self.root)

    main_screen = tk.PanedWindow(sashrelief=tk.GROOVE, sashwidth=4)
    left_frame = tk.ttk.Frame(main_screen)
    main_screen.add(left_frame)
    right_frame = tk.ttk.Frame(main_screen)
    main_screen.add(right_frame)
    main_screen.paneconfig(left_frame, minsize=200)
    main_screen.paneconfig(right_frame, minsize=100)

    status_line = tk.ttk.Frame(self.root)

    main_screen.grid(row=0, sticky=tk.W + tk.E + tk.N + tk.S)
    status_line.grid(row=1, sticky=tk.W + tk.E)

    tk.ttk.Label(left_frame, text="Video input:", font=(None, 11)).pack()
    self.canvas = ResizingCanvas(left_frame)
    self.canvas.pack(expand=True, fill=tk.BOTH)

    tk.ttk.Label(right_frame, text="Super resolution faces:", font=(None, 11)).pack()

    self.btn_snapshot=tk.Button(status_line, text="Take snapshot", command=self.snapshot)
    self.btn_snapshot.pack(side=tk.LEFT)
    self.status_text= tk.ttk.Label(status_line, text="Status")
    self.status_text.pack(side=tk.LEFT, fill=tk.X)

    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)

    self.delay = 15
    self.update()

    self.root.mainloop()


  def _addMenuBar(self, window):
    menu = tk.Menu(window)
    window.config(menu=menu)

    filemenu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Get camera feed", command=self.useCamera)
    filemenu.add_command(label="Open movie file...", command=self.openFile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=window.quit)

    helpmenu = tk.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About")


  def useCamera(self):
    self.vid = MyVideoCapture(0)


  def openFile(self):
    video_source = tk.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("movie files","*.avi"),("all files","*.*")))
    self.vid = MyVideoCapture(video_source)


  # Get a frame from the video source
  def snapshot(self):
    frame = self.vid.currentFrame
    if frame:
      cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))


  def update(self):
    ret, frame = self.vid.get_frame()

    if ret:
      pil_image = PIL.Image.fromarray(frame)

      self.canvas.update()
      max_width = self.canvas.winfo_width()
      max_height = self.canvas.winfo_height()
      if ((max_width > 1) and (max_height > 1)):
        pil_image.thumbnail((max_width, max_height), PIL.Image.ANTIALIAS)
        
      self.photo = PIL.ImageTk.PhotoImage(image=pil_image)
      self.canvas_img = self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW) 

    self.root.after(self.delay, self.update)


App(tk.Tk(), "First Test")
