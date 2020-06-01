from ..helper import running_on_jetson_nano

if running_on_jetson_nano():
  from .use_jetson_optimized import FaceDetectionNet
else:
  from .use_dlib import FaceDetectionNet
