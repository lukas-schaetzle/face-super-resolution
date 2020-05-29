import threading, time, cv2, multiprocessing, numpy, jetson.utils
from modules.helper import *
from modules.face_detection import FaceDetectionNet
from modules.face_super_res import FaceSuperResolutionNet
from timeit import default_timer as timer

def use_worker(send_queue, recv_queue):
  send_queue.cancel_join_thread()
  recv_queue.cancel_join_thread()
  vid_worker = VideoWorker(send_queue, recv_queue)
  vid_worker.work()

class VideoProcessInterface():
  def __init__(self, send_queue, recv_queue):
    self.send_queue = send_queue
    self.recv_queue = recv_queue
    self.process = multiprocessing.Process(target=use_worker, args=(recv_queue, send_queue))

class VideoWorker():
  FPS_INTERVAL = 1.5 # in seconds
  IDLE_SLEEP_TIME = 0.1 # in seconds
  GSTREAMER_PIPELINE = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=1280, height=720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'

  def __init__(self, send_queue, recv_queue):
    self.send_queue = send_queue
    self.recv_queue = recv_queue
    self.abort = False
    self.vid = None
    self.face_detection_net = FaceDetectionNet()
    self.face_super_res_net = FaceSuperResolutionNet()

  def work(self):
    print("Worker initialized")

    while (not self.abort):
      if (self.vid):
        self.next_frame()
        self.handle_fps_and_psnr()
      else:
        time.sleep(self.IDLE_SLEEP_TIME)
      self.handle_incoming_msg()

  def handle_incoming_msg(self):
    messages = getNextEvents(self.recv_queue)
    for msg in messages:
      if (msg.topic == RcvTopic.KILL):
        self.abort = True
      elif (msg.topic == RcvTopic.USE_CAMERA):
        self.use_camera()
      elif (msg.topic == RcvTopic.OPEN_FILE):
        self.open_file(msg.content)
      elif (msg.topic == RcvTopic.END_VID):
        self.end_video()
      else:
        print("No endpoint for event topic {topic}".format(topic=msg.topic))

  def use_camera(self):
    access_success = True
    self.cam = jetson.utils.gstCamera(640, 360, "0")

    # try:
    #   print("Trying to use standard camera")
    #   self.new_video(0)
    # except ValueError:
    #   try:
    #     print("Trying to use gStreamer camera")
    #     self.new_video(self.GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
    #   except ValueError:
    #     access_success = False

    # if (self.vid.read() and access_success):
    #   self.send_queue.put_nowait(QueueMsg(SndTopic.MSG, "Using camera feed"))
    # else:
    #   self.send_queue.put_nowait(QueueMsg(SndTopic.MSG_ERROR, "Could not use camera"))
    #   self.vid = None

  def open_file(self, filename):
    print(filename)
    try:
      self.new_video(filename)
      self.send_queue.put_nowait(QueueMsg(SndTopic.MSG, "Using file " + filename))
    except ValueError:
      self.send_queue.put_nowait(QueueMsg(SndTopic.MSG_ERROR, "Could not open file " + filename))
      
  def new_video(self, video_source):
    self.vid = cv2.VideoCapture(video_source)
    if (not (self.vid and self.vid.isOpened())):
      self.vid = None
      raise ValueError("Unable to open video source")

    self.frame_counter = 0
    self.psnr_log = [0, 0]
    self.last_timer_value = timer()

  def handle_fps_and_psnr(self):
    current_time = timer()
    time_since_last_calc = current_time - self.last_timer_value

    if (time_since_last_calc >= self.FPS_INTERVAL):
      self.handle_fps(current_time, time_since_last_calc)
      self.handle_psnr()

  def handle_fps(self, current_time, time_since_last_calc):
    self.fps = self.frame_counter / time_since_last_calc
    self.last_timer_value = current_time
    self.frame_counter = 0

    self.send_queue.put_nowait(QueueMsg(
      SndTopic.FPS, "{fps:.2f}".format(fps=self.fps)
    ))

  def handle_psnr(self):
    if (self.psnr_log[1] > 0):
      self.psnr = self.psnr_log[0] / self.psnr_log[1]
      self.psnr_log = [0, 0]

      self.send_queue.put_nowait(QueueMsg(
        SndTopic.PSNR, "{psnr:.2f}".format(psnr=self.psnr)
      ))

  def handle_psnr(self):
    if (self.psnr_log[1] > 0):
      self.psnr = self.psnr_log[0] / self.psnr_log[1]
      self.psnr_log = [0, 0]

      if (not self.abort):
        self.send_queue.put_nowait(QueueMsg(
          SndTopic.PSNR, "{psnr:.2f}".format(psnr=self.psnr)
        ))

  def next_frame(self):
    imgRaw, width, height = self.cam.CaptureRGBA(zeroCopy=1)
    face_locations = self.face_detection_net.infer(imgRaw)

    img = jetson.utils.cudaToNumpy(imgRaw, width, height, 4)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB).astype(numpy.uint8)
    self.current_frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    annotatedFrame = self.current_frame.copy()

    self.super_res_faces = []
    for index, face in enumerate(face_locations, 1):
      cropped_face = cv2.resize(
        frame[face.top:face.bottom, face.left:face.right],
        (128, 128)
      )
      # downscaled_face = downscale_to_16x16(cropped_face)
      # super_res_face = self.face_super_res_net.infer(downscaled_face)

      # psnr = cv2.PSNR(cropped_face, super_res_face)
      # self.psnr_log[0] += psnr
      # self.psnr_log[1] += 1

      # self.draw_rect(annotatedFrame, (face.left, face.top), (face.right, face.bottom), index)
      # self.super_res_faces.append(SuperResFaceResult(
      #   cropped_face,
      #   downscaled_face,
      #   super_res_face,
      #   psnr
      # ))

    self.current_frame = frame
    self.current_frame_annotated = annotatedFrame
    self.frame_counter += 1

    if (not self.abort):
      self.send_queue.put_nowait(QueueMsg(
        SndTopic.NEXT_FRAME,
        ResultImages(self.current_frame, self.current_frame_annotated, self.super_res_faces)
      ))

  def draw_rect(self, img, origin, end, descr, color=(220, 20, 60)):
    cv2.rectangle(img, origin, end, color, 2)

    descr = str(descr)
    (text_width, text_height), baseline = cv2.getTextSize(descr, cv2.FONT_ITALIC, 1, 2)
    text_height += baseline
    cv2.rectangle(img, origin, (origin[0] + text_width, origin[1] + text_height), color, cv2.FILLED)
    cv2.putText(img, descr, (origin[0], origin[1] + text_height - int(baseline/2)), cv2.FONT_ITALIC, 1, (255, 255, 255), 2)

  def end_video(self):
    self.vid = None
    self.send_queue.put_nowait(QueueMsg(SndTopic.VIDEO_END))
