import jetson.inference, jetson.utils, cv2, numpy
from ..helper import FaceArea, upscaleTuple, resizeImage

class FaceDetectionNet():
  def __init__(self):
    self.net = jetson.inference.detectNet("facenet", threshold=0.5)

  def infer(self, input_img):
    face_locations = self.net.Detect(input_img, 640, 360, "True")

    faces = []
    for face in face_locations:
      upscaled_coords = (face.Left, face.Top, face.Right, face.Bottom)
      faces.append(FaceArea(upscaled_coords, max_dim=(max_width, max_height)))
    return faces
