# EVA
Lego robot control program which contains the following features:
- The robot follows the infrared beacon.
- The robot moves along the drawn curved line.
- The robot moves along a specified path.
- A set of tools for auto-tuning the parameters of the robot.

## How to prepare the ev3dev environment.
All steps on how to prepare the environment for the EV3 robot described here: https://www.ev3dev.org/docs/getting-started/.

## Deployment.
To deploy a new version to the robot need to do the following:
1. Connect the robot to the USB connector.
2. Connect to the robot by SSH with the following parameters:
    - Host: ev3dev
    - Login: robot
    - Password: maker
3. Upload the new version to the /root.

## Commands.
All robot programs placed in the root directory and the following programs supported:
- The robot follows the infrared beacon: follower.py.
- The robot moves along the drawn curved line: trolley.py.
- The robot moves along a specified path: traveler.py.

All auto-tuning programs placed in the /root/tune and the following programs supported:
- Tune motion parameters: tune_motion.py.
- Tune infrared sensor parameters: tune_infrared_sensor.py.
- Tune color sensor parameters: tune_color_sensor.py
- Tune PID regulator for moving along a line: tune_trolley_pid_regulator.py
- Tune velocity for moving along a line: tune_trolley_velocity.py

### Run command.
To run the program you need to choose a program in 'File Browser' on the EV3 and execute it.
