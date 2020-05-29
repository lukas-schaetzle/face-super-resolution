import torch, face_recognition
from ..helper import FaceArea, upscaleTuple, resizeImage

class FaceDetectionNet():
  def __init__(self):
    self.model = 'cnn' if torch.cuda.is_available() else 'hog'

  def infer(self, input_img):
    max_height, max_width = input_img.shape[:2]

    small_frame, scale_factor = resizeImage(input_img, 640, 360)
    reverse_scale_factor = 1 / scale_factor
    face_locations = face_recognition.face_locations(small_frame, model=self.model)

    faces = []
    for (top, right, bottom, left) in face_locations:
      upscaled_coords = upscaleTuple(reverse_scale_factor, (left, top, right, bottom))
      faces.append(FaceArea(upscaled_coords, max_dim=(max_width, max_height)))
    return faces
