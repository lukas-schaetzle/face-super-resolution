import cv2
import PIL.Image, PIL.ImageTk

class MyVideoCapture:
  def __init__(self, video_source=0):
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
 
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.current_frame = None
    self.super_res_faces = []
 
  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()

  def get_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      # Hier kommt das aktuelle frame des Videos
      if ret:
        """
        TODO
         in self.current_frame muss das annotierte Bild rein
         die vergrößerten Bilder sollten dann das Attribut super_res_faces überschreiben
        """
        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return (ret, self.current_frame)
      else:
        return (ret, None)
    else:
      return (ret, None)
