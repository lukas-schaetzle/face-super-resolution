import torch
from facenet_pytorch import MTCNN
from PIL import Image
from ..helper import FaceArea, upscaleTuple
import cv2

def resizeImage(cv_img, max_width, max_height, interpolation=cv2.INTER_LINEAR):
  height, width = cv_img.shape[:2]

  h_ratio = max_height / height
  w_ratio = max_width / width
  scale_factor = max(h_ratio, w_ratio)
  return cv2.resize(cv_img, (0,0), fx=scale_factor, fy=scale_factor, interpolation=interpolation), scale_factor

class FaceDetectionNet():
  def __init__(self):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    self.model =  MTCNN(keep_all=True, device=device)

  def infer(self, input_img):
    max_height, max_width = input_img.shape[:2]

    small_frame, scale_factor = resizeImage(input_img, 640, 360)
    reverse_scale_factor = 1 / scale_factor
    face_locations, _ = self.model.detect(Image.fromarray(small_frame))

    faces = []
    for box in face_locations:
      (left, top, right, bottom) = box.tolist()
      upscaled_coords = upscaleTuple(reverse_scale_factor, (left, top, right, bottom))
      faces.append(FaceArea(upscaled_coords, max_dim=(max_width, max_height)))
    return faces
