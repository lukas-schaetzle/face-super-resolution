import cv2

class MyVideoCapture:
  def __init__(self, video_source=0):
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
 
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.current_frame = None
    self.current_frame_annotated = None
    self.super_res_faces = []
 
  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()

  def next_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      # Hier kommt das aktuelle frame des Videos
      
      if ret:
        annotatedFrame = frame.copy()
        self.draw_rect(annotatedFrame, (20, 20), (100, 100), "1")
        
        """
        TODO
         in annotatedFrame muss das annotierte Bild rein
         die vergrößerten Bilder sollten dann das Attribut super_res_faces überschreiben
        """

        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.current_frame_annotated = cv2.cvtColor(annotatedFrame, cv2.COLOR_BGR2RGB)

  def get_current_frame(self, with_annotations=True):
    return self.current_frame_annotated if with_annotations else self.current_frame

  def draw_rect(self, img, origin, end, descr, color=(18, 156, 243)):
    cv2.rectangle(img, origin, end, color, 2)

    (text_width, text_height), baseline = cv2.getTextSize(descr, cv2.FONT_ITALIC, 0.5, 1)
    text_height += baseline
    cv2.rectangle(img, origin, (origin[0] + text_width, origin[1] + text_height), color, cv2.FILLED)
    cv2.putText(img, descr, (origin[0], origin[1] + text_height - baseline), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
