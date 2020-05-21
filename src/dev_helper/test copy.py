import multiprocessing, time, cv2

def work(queue):
  print("a")
  time.sleep(5)
  print("b")
  print(queue.get_nowait())
  print("Ende")

class Test(multiprocessing.Process):
  def __init__(self, queue):
    super().__init__()
    self.queue = queue

  def run(self):
    self.a = 1
    print(self.queue.get())
    print(self.a)

if __name__ == "__main__":
  vid = cv2.VideoCapture("tesjkjt")
  print(str(vid))
  if vid.isOpened():
    print("jo")
    ret, frame = vid.read()
  queue = multiprocessing.Queue()
  process = Test(queue)
  process.start()

  queue.put(1)
  time.sleep(5)
