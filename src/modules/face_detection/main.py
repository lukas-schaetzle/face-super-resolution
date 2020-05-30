import jetson.inference, jetson.utils, cv2, numpy
from ..helper import FaceArea, upscaleTuple, resizeImage, debug_log

class FaceDetectionNet():
  SMALL_DIM = (640, 360)

  def __init__(self):
    debug_log("Init face detection net")
    self.net = jetson.inference.detectNet("facenet", threshold=0.5)

  def infer(self, input_img):
    max_height, max_width = input_img.shape[:2]

    input_img_rgba = cv2.cvtColor(input_img, cv2.COLOR_RGB2RGBA)
    small_frame, scale_factor = resizeImage(input_img_rgba, self.SMALL_DIM[0], self.SMALL_DIM[1])
    reverse_scale_factor = 1 / scale_factor

    debug_log("Begin cuda conversion")
    cuda_img = jetson.utils.cudaFromNumpy(small_frame.astype(numpy.float32))
    debug_log("End cuda conversion")
    face_locations = self.net.Detect(cuda_img, self.SMALL_DIM[0], self.SMALL_DIM[1], "False")

    faces = []
    for face in face_locations:
      upscaled_coords = upscaleTuple(reverse_scale_factor, (face.Left, face.Top, face.Right, face.Bottom))
      faces.append(FaceArea(upscaled_coords, max_dim=(max_width, max_height)))
    return faces
