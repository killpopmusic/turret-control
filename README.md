# RC Airsoft Sentry Turret 

## Overview 
This is a repository containing control scripts for an autonomous turret project. The first version of the project was meant to run entirely on Raspberry Pi 4b with the camera: PiCamera module 3. Other hardware may be used, though the configuration may vary. \
The repository contains seperate folders with vision algorithm and algorithms for testing separate functionalities of the turret such as: manual servo movement, continuous auto servo movement, shooting with the gearbox.\
\
It is highly recommended to test each functionality before running the main program.

## OS
+ RPi OS: Raspbian Bullseye or newer
+ Host PC: Ubuntu 22.04 recommended

## Software setup
### Step 1: Connect and Verify the Camera

1. **Connect the Camera**
   - Attach the camera to your Raspberry Pi using the appropriate interface.

2. **Verify Camera Detection**
   - Ensure the system detects the camera by running the following command:
     ```sh
     rpicam-still
     ```
   - If the camera is not detected, you may need to manually enable the camera interface:
     ```sh
     sudo raspi-config
     ```
     - Navigate to `Interfacing Options` and select `Camera`, then choose `Yes` to enable it.

### Step 2: Install Required Libraries

1. **Install libcamera**
   - The `libcamera` library should be pre-installed on Raspbian. If it is not installed, it may cause issues.

2. **Install picamera2**
   - Install the `picamera2` library, a Python wrapper for the C++ API to handle the camera:
     ```sh
     sudo apt install python3-libcamera
     sudo apt install python3-picamera2
     ```

### Step 3: Install and Configure OpenCV in a Virtual Environment

1. **Install virtualenv**
   - Install the `virtualenv` package to create a virtual environment:
     ```sh
     pip install virtualenv
     ```

2. **Create a Virtual Environment**
   - Create a virtual environment to avoid conflicts with system packages:
     ```sh
     virtualenv env --system-site-packages
     ```

   - This creates a directory named `env` that will contain the necessary packages and has access to the external camera libraries.

3. **Activate the Virtual Environment**
   - Enter the virtual environment:
     ```sh
     source env/bin/activate
     ```

4. **Install OpenCV**
   - Install the OpenCV package within the virtual environment:
     ```sh
     pip install opencv-python-headless
     ```

## Startup 
### Connection and testing turret's functions
The turret can work remotely, for that a SSh connection between RPi and host PC needs to be established:
+Make sure that the SSH is enabled on the Rpi, then setup the connection on RPi to the same network as the host.
+ On host PC terminal:
  ```
  ssh username@raspberrypi.local
  ```
+Activate the virtual environment 
+Clone this repository into desired directory 
+ ```
  cd turret-control
  ```
  ```
  cd Testing scripts
  ```
+ Each script can be run using
  ```
  python3 name_of_the_script.py

  '''

### Running the main script
  ```
  python3 main.py

  '''
  
