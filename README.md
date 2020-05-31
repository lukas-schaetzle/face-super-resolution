# IW276 Autonome Systeme Labor - Face Super-Resolution on Jetson Nano

![Screenshot Program](https://github.com/Tummerhore/face-super-resolution/blob/master/readme_images/ScreenshotProgram.png?raw=true)

> This work was done by Lukas Schätzle, Jacqueline Wegert, Benno Latermann during the IWI276 Autonome Systeme Labor at the Karlsruhe University of Applied Sciences (Hochschule Karlruhe - Technik und Wirtschaft) in SS 2020. 


## Table of Contents

* [Requirements](#requirements)
* [Preparations for Jetson Nano](#preparations-for-jetson-nano)
* [Running the programl](#running-the-program)
* [Running on a normal PC](#running-on-a-normal-PC-experimental)
* [Acknowledgments](#acknowledgments)
* [Contact](#contact)

## Requirements

* Python 3.6 or above
* Jetson Nano (additional experimental version for normal PC exists, too)

## Preparations for Jetson Nano:

**Note:** If you want to run the program on a normal desktop PC, follow the instructions in section [Running on a normal PC](#running-on-a-normal-PC-experimental) instead.

Go to https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-repo-2.md and install the necessary dependencies. The following sections are relevant:
* Cloning the Repo
* Python Development Packages
* Configuring with CMake
* Downloading Models (make sure that model "FaceNet" is selected, included by default)
* Installing PyTorch (make sure to select PyTorch 1.4.0 for Python 3.6, this is *not* selected by default!)

![Screenshot PyTorch installer](https://github.com/Tummerhore/face-super-resolution/blob/master/readme_images/ScreenshotPytorchInstallation.png?raw=true)

* Compiling the Project

To display the current power usage and temperature you also have to install the package "jetsons-stats": `sudo -H pip3 install -U jetson-stats`

## Running the program

If you want to use a camera, connect it in advance. (The program has been successfully tested with a USB camera. It may also work with a MIPI camera, but we cannot guarantee it.) If you have no camera, you can also use video and image files.

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

**Note:** The Ubuntu distro which is installed on the Jetson Nano uses a global menu bar by default (like MacOS). You can access it from the panel at the very top of your screen.

## Running on a normal PC (experimental)

To install the dependencies on a normal pc we have created a pipenv file. Please note that the temperature and power usage display will not work here. Also, the program will use a different neural network for face detection, as the standard one (which is faster) needs a package specifically designed for the jetson.

To install dependencies just run `pipenv install` in the project's root directory. On Windows, pipenv may not be able to install all dependencies, you likely have to build dlib by yourself (see https://stackoverflow.com/a/49538054/10264920).

We also had some trouble installing pytorch through pipenv. I suggest using pip directly to install it with the mentioned install command on pytorch's website. E.g. `pipenv run pip install torch===1.5.0 torchvision===0.6.0 -f https://download.pytorch.org/whl/torch_stable.html`

After successfully installing the dependencies, run `pipenv run python3 src/main.py`

## Known issues

* MIPI camera might not work correctly. If you run into problems with it, use a USB camera as a workaround.
* The face recognition neural network is different for the normal pc version.
* Some bluish green (sometimes even red pixels) may appear on the right faces in the super resolution panel. These pixels appear when using the function `torchvision.transforms.ToPILImage` on the output of the super resolution net and seem to appear more often when the light is very bright in the frame.
* Sometimes opened jpg images are not correctly displayed

## Acknowledgments

This repo is based on
  - [Source 1](https://github.com/)
  - [Source 2](https://github.com/)
  - [Source 2](https://github.com/)

Thanks to the original authors for their work!

## Contact
Please email `mickael.cormier AT iosb.fraunhofer.de` for further questions.
