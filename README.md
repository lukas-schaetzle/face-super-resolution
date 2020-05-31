# Hochschule Karlsruhe: Autonome Systeme Labor SS20 - Face Super-Resolution (Jetson Nano)

This program has been made for the lab "Autonome Systeme" at Hochschule Karlsruhe - Technik und Wirtschaft during the summer semester 2020.

Minimal Python version is 3.6

## Preparations for Jetson Nano:

*Note*: If you want to run the program on a normal desktop PC, follow the instruction in section [Running on a desktop PC](#running-on-a-normal-PC-experimental) instead.

Go to https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-repo-2.md and install the necessary dependencies. The following sections are relevant:
* Cloning the Repo
* Python Development Packages
* Configuring with CMake
* Downloading Models (make sure that model "FaceNet" is selected, included by default)
* Installing PyTorch (make sure to select PyTorch 1.4.0 for Python 3.6, this is not the default!)

![Screenshot PyTorch installer](https://github.com/Tummerhore/face-super-resolution/blob/new_jetson_test/ScreenshotPytorchInstallation.png?raw=true)

* Compiling the Project

To display the current power usage and temperature you also have to install the package "jetsons-stats": `sudo -H pip3 install -U jetson-stats`

## Running the program

If you want to use a camera, connect it in advance. (The program has been successfully tested with a USB camera. It may also work with a MIPI camera, but we cannot guarantee it.) If you have no camera, you can also use video files.

From the project's root directory run: `python3 src/main.py`

You can pass the following parameters:
| Parameter   | Effect                                                                                                                |
|-----------	|---------------------------------------------------------------------------------------------------------------------	|
| --cam     	| Immediately open the camera feed once the neural networks are loaded so you do not have to choose it from the menu manually. 	|
| --debug   	| Print debug messages in the terminal                                                                                	|

Once the program window is open, the neural networks are initialized. This may take quite some time. Especially, when running the program for the first time as TensorRT then optimizes one neural network for later use. After initialization, the statusbar will show the message: "Worker initialized". You can now open the camera or a video file through the menu (`File -> Get camera feed / Open video file`)

The left panel shows the input video with annotated faces. (You can also the annoatations through the menu: `View -> Show annotations`). The right panel shows from left to right:
* Extracted face
* Downscaled face to 16*16 px which is used as input for the face super resolution net
* Output from the face super resolution net

At the bottom left, you can see several performance values.

At any time, you can take a snapshot to save the current input and output images along with the according PSNR values per face. Use the spacebar or the menu (`File -> Save snapshot`). The status bar will tell you where the snapshot has been saved to.

## Running on a normal PC (experimental)

To install the dependencies on a normal pc we have created a pipenv file. Please note that the temperature and power usage display will not work here. Also, the program will use a different neural network for face detection, as the standard one (which is faster) needs a package specifically designed for the jetson.

To install dependencies just run `pipenv install` in the project's root directory. On Windows, pipenv may not be able to install all dependencies, you likely have to build dlib by yourself (see https://stackoverflow.com/a/49538054/10264920).

We also had some trouble installing pytorch through pipenv. I suggest using pip directly to install it with the mentioned install command on pytorch's website. E.g. `pipenv run pip install torch===1.5.0 torchvision===0.6.0 -f https://download.pytorch.org/whl/torch_stable.html`

After successfully installing the dependencies, run `pipenv run python3 src/main.py`

## Known issues

* MIPI camera might not work correctly. If you run into problems with it, use a USB camera as a workaround.
* The face recognition neural network is different for the normal pc version.
