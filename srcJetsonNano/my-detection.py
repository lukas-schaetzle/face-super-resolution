# source: https://www.youtube.com/watch?v=bcM5AQSAzUY
# modules used for object detection and camera capture
import jetson.inference
import jetson.utils

# the string represents the detection model, can be replaced, see link below
# https://github.com/dusty-nv/jetson-inference/blob/master/docs/detectnet-console-2.md#pre-trained-detection-models-available
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

# the last parameter is the device file, can be find out with the command:  v4l2-ctl --list-devices (you need to install the package first: sudo apt-get install v4l-utils), with command v4l2-ctl --device /dev/video0 --list-formats-ext you see all the valid resolution of the camera
camera = jetson.utils.gstCamera(640, 360, "/dev/video0")
#camera = jetson.utils.gstCamera(1024, 768, "0")

# OpenGL display window for rendering the results
display = jetson.utils.glDisplay()

while display.IsOpen():
	# returns image
	img, width, height = camera.CaptureRGBA()
	# the detection network processes the image
	detections = net.Detect(img, width, height)
	display.RenderOnce(img, width, height)
	display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
