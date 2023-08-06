# cognifly-python
Control the CogniFly open-source drone remotely from your python script.

## Quick links

- [Prerequisite](#prerequisite)
  - [Drone setup instructions](/readme/DRONE_SETUP.md)
- [Installation](#installation)
- [Usage](#usage)
  - [Pro API](#pro-api)
  - [School API](#school-api)
  - [Streaming](#streaming)
- [Troubleshooting](#troubleshooting)

## Prerequisite
This readme will guide you through the steps to install and use the `cognifly-python` library on a readily setup CogniFly drone. If your drone is not setup yet, please first follow the [drone setup instructions](/readme/DRONE_SETUP.md).

- The library requires python >= 3.7

If you followed the [drone setup instructions](/readme/DRONE_SETUP.md), you can ignore the remainder of this section.

### Requirements on the Raspberry Pi

- On the Raspberry Pi, execute the following:
  ```terminal
  sudo apt-get update
  sudo apt-get install libatlas-base-dev libopenjp2-7 libtiff5 python3-pip
  ```
- If you wish to use streaming, a pi camera must be connected to the raspberry pi and working properly.


### Requirements on the Flight Controller

- The drone must execute the [CogniFly fork of INAV](https://github.com/thecognifly/inav/tree/CogniFly)
- The drone must be set in "EST_POS" debug mode for this library to work
To ensure this, connect CogniFly to `inav-configurator`, do to the CLI tab, and execute the following:
```bash
set debug_mode = EST_POS
save
```

## Installation

`cognifly-python` can be installed from PyPI.
This is done by simply executing the following on both the Raspberry Pi and the remote-controlling computer:

```bash
pip3 install --upgrade pip
pip3 install cognifly
```

## Usage

In order to use the installed library, the `cognifly_controller.py` script must first be running on Cognifly.
At the moment, this can be done by connection to the drone through SSH, and executing the following command:

```bash
cognifly-controller
```

A service may be set on the rapsberri pi to launch this script automatically on CogniFly at startup, so that the user doesn't need to SSH the drone.

*Note: On the Raspberry Pi, the `cognifly-controller` command may not become available immediately after installation. If not, try closing the terminal and opening a new one.
Worst case scenario, this command is an alias for `python3 -m cognifly controller`.*


### Manual control (optional)

It is possible to manually control the drone with the keyboard via SSH, by focusing the session that executes `cognifly_controller.py` on the raspberry pi:

- `A`: arm
- `D`: disarm
- `T`: take off
- `L`: land
- `8`: forward
- `5`: backward
- `7`: left
- `9`: right
- `4`: left yaw
- `6`: right yaw
- `pageup`: up
- `pagedown`: down
- `R`: reset the board and exit the script

### Remote control

The remote control API is defined in [cognifly_remote.py](https://github.com/thecognifly/cognifly-python/blob/main/cognifly/cognifly_remote/cognifly_remote.py) (please read the docstrings for thorough documentation).

Connecting to the drone is as simple as creating a `Cognifly` object.
By default, this will also pop a simple Graphic User Interface, that can be used to disarm the drone on the event of an emergency, and to visualize the camera stream when activated:

```python
from cognifly import Cognifly

# connect to the drone and pop the GUI:
cf = Cognifly(drone_hostname="my_drone_name.local")

time.sleep(10.0)
```



The API is divided into a "pro" and a "school" API.

#### Pro API

The "pro" API is fairly simple and is what you should use for serious applications.
It enables the user to control Cognifly either by velocity or by position, in two possible coordinate systems:
- world frame: X and Y relative to the starting point of the drone, Yaw relative to the starting orientation of the drone, and Z relative to the ground,
- drone frame: X, Y and Yaw relative to the current position and orientation of the drone, and Z relative to the ground.

Example-script using the "pro" API for control:

```python
import time
from cognifly import Cognifly

# create a Cognifly object (resets the controller):
cf = Cognifly(drone_hostname="my_drone_name.local")

# arm the drone:
cf.arm()
time.sleep(1.0)

# take off to default altitude :
cf.takeoff_nonblocking()
time.sleep(10.0)

# go 0.2 m/s frontward for 1.0 second:
cf.set_velocity_nonblocking(v_x=0.2, v_y=0.0, v_z=0.0, w=0.0, duration=1.0, drone_frame=True)
time.sleep(2.0)

# go rightward and upward while rotating for 1.0 second:
cf.set_velocity_nonblocking(v_x=0.0, v_y=0.2, v_z=0.1, w=0.5, duration=1.0, drone_frame=True)
time.sleep(2.0)

# retrieve battery, pose, speed and health flags:
telemetry = cf.get_telemetry()
print(f"telemetry:\n{telemetry}")

# go to (-0.5, -0.5, 0.5) and back to the initial yaw (0.0) at a max speed of 0.25 m/s, 0.5 rad/s:
cf.set_position_nonblocking(x=-0.5, y=-0.5, z=0.5, yaw=0.0,
                            max_velocity=0.25, max_yaw_rate=0.5, max_duration=10.0, relative=False)
time.sleep(5.0)

# go frontward for 0.5 m at 0.25 m/s, staying at an altitude of 0.5 m:
cf.set_position_nonblocking(x=0.5, y=0.0, z=0.5, yaw=0.0,
                            max_velocity=0.25, max_yaw_rate=0.5, max_duration=10.0, relative=True)
time.sleep(5.0)

# go back home:
cf.set_position_nonblocking(x=0.0, y=0.0, z=0.5, yaw=0.0,
                            max_velocity=0.25, max_yaw_rate=0.5, max_duration=10.0, relative=False)
time.sleep(5.0)

# land:
cf.land_nonblocking()
time.sleep(2.0)

# disarm the drone
cf.disarm()

# reset the drone (reinitializes coordinate system):
cf.reset()
```

Note that this API is non-blocking, a new call will override the previous call
(position and velocity are controlled by PIDs, so violent changes WILL make the drone unstable).

#### School API

The "school" API is an overlay of the "pro" API, built for students who need an easy and relatively safe API for class purpose.
It is vastly inspired from the `easytello` library, of which it reproduces most of the interface, adapted to Cognifly.
Contrary to the "pro" API, calls to the "school" API are blocking and return only when the command has been fully performed (or when it times out).
It mostly consists of hidden calls to the position control "pro" API with an additional hidden callback through the `sleep_until_done` method (see the code to reproduce similar behavior with the "pro" API).

Whereas the units of the "pro" API are meters and radians, the units of the "school" API are centimeters and degrees.

Example using the "school" API for control:
```python
from cognifly import Cognifly

# create a Cognifly object (resets the controller):
cf = Cognifly(drone_hostname="my_drone_name.local")

# take off (resets the controller):
cf.takeoff()

# go forward for 50 cm:
cf.forward(50)

# turn clockwise by 90 degrees:
cf.cw(90)

# turn counter-clockwise by 45 degrees:
cf.ccw(45)

# other movements:
cf.backward(20)
cf.up(30)
cf.down(20)
cf.right(20)
cf.left(10)

# go to (0, 0, 0.5) (cm) with a yaw of 90° counter-clockwise compared to the initial orientation
cf.go(0, 0, 0.5, -90)

# sequence of position targets (when 4 items, the last is yaw):
cf.position_sequence([[0.2, 0.2, 0.5, 0.0],
                      [0.0, 0.1, 0.5],
                      [0.0, 0.0, 0.5]])

# get telemetry:
battery = cf.get_battery()
height = cf.get_height()
speed = cf.get_speed()
x, y, z = cf.get_position()
vx, vy, vz = cf.get_velocity()

# land (disarms the drone):
cf.land()
```

#### Streaming

Cognifly can stream from the raspberry pi camera (note: frames are transferred directly through the local network).
First make sure that the camera is enabled in the raspberry pi, and that it works correctly.

It is possible to display the video or to retrieve frames for processing:

```python
from cognifly import Cognifly

# create a Cognifly object (resets the controller):
cf = Cognifly(drone_hostname="my_drone_name.local")

# take off (resets the controller):
cf.takeoff()

# display the stream at 24 fps:
cf.stream(fps=24)
time.sleep(10.0)

# stop the stream:
cf.streamoff()
time.sleep(5.0)

# turn the stream on at 5 fps, with no display:
cf.streamon(fps=5)

# retrieve a frame for processing:
cv2_image = cf.get_frame()

# turn the stream off:
cf.streamoff()

# land:
cf.land()
```

## Troubleshooting
**Drift**: A slight horizontal drift of less than 1cm/s is to be expected.
However, if the drone drifts badly, disarm it, move it around and check that the position and velocity estimates make sense.
- If some estimates remain fixed: the drone is probably not in EST_POS debug mode. Carefully setup the flight controller again, according to the [drone setup instructions](/readme/DRONE_SETUP.md).
- If some estimates behave crazily: the floor is probably not textured enough. The current iteration of CogniFly uses a cheap optical flow sensor to estimate its location, and this sensor needs a lot of texture on the ground to work properly.
