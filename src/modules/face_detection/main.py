import jetson.inference, jetson.utils, cv2, numpy
from ..helper import FaceArea, upscaleTuple, resizeImage

class FaceDetectionNet():
  def __init__(self):
    self.net = jetson.inference.detectNet("facenet", threshold=0.5)

  def infer(self, input_img):
    max_height, max_width = input_img.shape[:2]

    input_img_rgba = cv2.cvtColor(input_img, cv2.COLOR_RGB2RGBA)
    small_frame, scale_factor = resizeImage(input_img_rgba, 640, 360)
    reverse_scale_factor = 1 / scale_factor

    cuda_img = jetson.utils.cudaFromNumpy(small_frame).astype(numpy.float32)
    face_locations = self.net.Detect(cuda_img, 640, 360)

    faces = []
    for face in face_locations:
      upscaled_coords = upscaleTuple(reverse_scale_factor, (face.Left, face.Top, face.Right, face.Bottom))
      faces.append(FaceArea(upscaled_coords, max_dim=(max_width, max_height)))
    return faces
