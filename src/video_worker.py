import threading, platform, time, cv2, jetson.inference, jetson.utils
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from helper import getPath, ResultImages
from timeit import default_timer as timer
import numpy as np

import torch
from model import Generator
from PIL import Image
import torchvision.transforms as transforms
from torchvision import utils

class VideoWorker(QObject):
  sig_fps = pyqtSignal(str) 
  sig_next_frame = pyqtSignal(ResultImages)

  def __init__(self, video_source=0, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._abort = False
    self._confidence = 0.75
    self._camWidth = 1280
    self._camHeight = 720

    self._frame_counter = 0
    self._last_timer_value = None
    self.fps = None

    self.vid = None
    self.current_frame = None
    self.current_frame_annotated = None
    self.super_res_faces = [QtGui.QPixmap(getPath("assets", "test.png")) for x in range(4)]

    if (self.is_jetson):
      self.cam = jetson.utils.gstCamera(self._camWidth, self._camHeight, "0")
    else:
      self.cam = jetson.utils.gstCamera(self._camWidth, self._camHeight, "/dev/video0")
    
    self.net = jetson.inference.detectNet("facenet", threshold=self._confidence)

    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.generator = Generator().to(self.device)
    self.generator.eval()
    g_checkpoint = torch.load("./checkpoints/generator_checkpoint_singleGPU.ckpt")
    self.generator.load_state_dict(g_checkpoint['model_state_dict'], strict=False)
    self.step = g_checkpoint['step']
    self.alpha = g_checkpoint['alpha']
    self.iteration = g_checkpoint['iteration']
    self._16x16_down_sampling = transforms.Resize((16,16))
    self._32x32_down_sampling = transforms.Resize((32, 32))
    self._64x64_down_sampling = transforms.Resize((64, 64))
    self.totensor = transforms.Compose([transforms.ToTensor(),
                                   transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)), ])
    print('pre-trained model is loaded step:%d, alpha:%d iteration:%d'%(self.step, self.alpha, self.iteration))

  @pyqtSlot()
  def work(self):
    self._last_timer_value = timer()
    while (not self._abort):
      # TODO: stop when video file finished
      self.next_frame()
      self.calculate_fps()

      QtCore.QCoreApplication.processEvents()

    print("Thread stopped properly") # TODO: remove debug msg

  def calculate_fps(self):
    current_time = timer()
    time_since_last_calc = current_time - self._last_timer_value
    if (time_since_last_calc >= 1.5):
      self.fps = self._frame_counter / time_since_last_calc
      self._last_timer_value = current_time
      self._frame_counter = 0

      if (not self._abort):
        self.sig_fps.emit('%.2f'%(self.fps))

  def next_frame(self):
    imgRaw, width, height = self.cam.CaptureRGBA(zeroCopy=1)
    face_locations = self.net.Detect(imgRaw, width, height, "True")
    img = jetson.utils.cudaToNumpy(imgRaw, width, height, 4)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB).astype(np.uint8)
    self.current_frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    self.current_frame_annotated = self.current_frame.copy()

    cnt = 1
    for face in face_locations:
      if face.Confidence >= self._confidence:
        faceRect = self.getFaceArea(face)
        imgIdName = str(cnt)
        cv2.rectangle(self.current_frame_annotated, (faceRect[0], faceRect[1]), (faceRect[2], faceRect[3]), (0, 225, 250), 3)
        cv2.rectangle(self.current_frame_annotated, (faceRect[0], faceRect[1]), (faceRect[0] + 50, faceRect[1] + 50), (0, 225, 250), cv2.FILLED)
        cv2.putText(self.current_frame_annotated, imgIdName, (faceRect[0] + 10, faceRect[1] + 40), cv2.FONT_ITALIC, 1.5, (255, 255, 255), 3)
        print(face)
        print(faceRect)
        if (faceRect[2] - faceRect[0]) == (faceRect[3] - faceRect[1]):
          faceImg = img[faceRect[1]:faceRect[3], faceRect[0]:faceRect[2]]
          cv2.imwrite("face_" + imgIdName + ".jpg", faceImg)
          smallFaceImg = cv2.resize(faceImg, (16, 16))
          cv2.imwrite("smallFace_" + imgIdName + ".jpg", smallFaceImg)

          smallFaceImgPIL = Image.open("smallFace_" + imgIdName + ".jpg").convert('RGB')
          biggerFaceImg = self._16x16_down_sampling(self._32x32_down_sampling(self._64x64_down_sampling(smallFaceImgPIL)))
          biggerFaceImg = self.totensor(biggerFaceImg).unsqueeze(0).to(self.device)
          biggerFaceImg = self.generator(biggerFaceImg, self.step, self.alpha)
          utils.save_image(biggerFaceImg, "bigSmallFace_" + imgIdName + ".jpg")

          cnt += 1
    
    self._frame_counter += 1

    if (not self._abort):
      self.sig_next_frame.emit(ResultImages(self.current_frame, self.current_frame_annotated, self.super_res_faces))

  # struct left, top, bot, right, width, height
  def getFaceArea(self, face):
    sideLength = max(face.Width, face.Height)
    halfSideLength = sideLength / 2
    newCenter = face.Center + (0, sideLength / 3)
    return (max(0, int(newCenter[0] - halfSideLength)),
            max(0, int(newCenter[1] - halfSideLength)),
            min(self._camWidth, int(newCenter[0] + halfSideLength)),
            min(self._camHeight, int(newCenter[1] + halfSideLength)))

  def draw_rect(self, img, origin, end, descr, color=(18, 156, 243)):
    cv2.rectangle(img, origin, end, color, 2)
    (text_width, text_height), baseline = cv2.getTextSize(descr, cv2.FONT_ITALIC, 0.5, 1)
    text_height += baseline
    cv2.rectangle(img, origin, (origin[0] + text_width, origin[1] + text_height), color, cv2.FILLED)
    cv2.putText(img, descr, (origin[0], origin[1] + text_height - baseline), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)

  @pyqtSlot()
  def abort(self):
    self._abort = True

  def is_jetson():
    return platform.machine() == "aarch64"
