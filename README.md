# 6-DOF Pick-and-Place Robotic Arm

A vision-guided robotic arm designed to locate, pick up, move, and place objects within a defined workspace. The system combines a six-axis articulated mechanism, a vacuum end effector, a fixed camera, and software for simulation, vision, kinematics, and hardware control.

The arm's geometry is inspired by the kinematic dimension ratios of the KUKA KR 3 R540 and scaled for a smaller educational build. It is an independent student engineering project and is not affiliated with KUKA.

## Project Aim

The aim is to create a complete pick-and-place system that can:

1. Observe a workspace using a fixed camera.
2. Detect an object and determine its position.
3. Convert the detected position into the robot's coordinate system.
4. Calculate a valid arm pose for reaching the object.
5. Move the six joints to the required position.
6. Grip the object using a vacuum suction cup.
7. Transport it to a target location and release it.

The project is designed around modular subsystems so that the simulation, vision system, motion control, and end effector can be developed and tested independently before being combined.

## System Architecture

The robot is divided into three main physical systems supported by a software control layer:

| System | Purpose |
| --- | --- |
| Motion system | Positions and orients the end effector using six independently controlled joints |
| Vacuum effector system | Grips and releases objects using suction |
| Vision system | Detects objects and estimates their positions within the workspace |
| Software system | Simulates the arm, processes camera data, solves its motion, and coordinates the hardware |

## Motion System

The arm uses six revolute joints, giving it six degrees of freedom:

| Joint | Function |
| --- | --- |
| J1 | Rotates the entire arm about the base |
| J2 | Raises and lowers the upper arm at the shoulder |
| J3 | Extends and retracts the arm through the elbow |
| J4 | Rolls the wrist |
| J5 | Changes the wrist pitch |
| J6 | Rotates the end effector |

Together, the first three joints primarily determine the position of the wrist, while the final three determine the orientation of the suction tool. This allows the end effector to approach an object from a suitable direction rather than only reaching a point in space.

### Actuation and Feedback

The proposed design uses serial-bus smart servos containing an integrated motor, encoder, and control electronics. Position feedback allows the controller to compare commanded and measured joint angles instead of relying on unmeasured open-loop motion.

The base, shoulder, and elbow carry the largest loads and therefore require the highest torque. The current hardware concept considers:

- **Feetech STS3250 servos for J1-J3**, where higher torque is required
- **Feetech STS3215 servos for J4-J6**, where loading is lower

The servos are intended to share a daisy-chained TTL serial bus. Final actuator selection depends on calculated joint torque, payload, arm mass, acceleration, safety factor, and physical testing.

## Vacuum End Effector

The end effector is designed to handle suitable objects using a suction cup rather than a mechanical gripper.

The proposed pneumatic arrangement contains:

- A 12 V miniature vacuum pump for gripping
- A second pump for introducing air and releasing the object
- A suction cup connected through silicone tubing
- A Y-connector joining the pump lines to the suction line
- Separate MOSFET switches for independent pump control

The controller activates the vacuum pump when an object is collected. At the placement position, the vacuum is disabled and the release pump can briefly introduce air to separate the object from the suction cup more reliably.

This approach reduces the mechanical complexity of the tool, although its effectiveness depends on the object's surface area, shape, porosity, mass, and orientation.

## Vision System

A fixed-position USB camera observes the robot's working area. A stationary camera is preferred because its position relative to the workspace remains constant, making calibration simpler than with a camera mounted on the moving arm.

The vision software is written in Python using OpenCV. Its responsibilities include:

- Connecting to and configuring the camera
- Capturing and displaying live frames
- Detecting objects within the workspace
- Drawing labels and detection regions on the camera view
- Estimating the image coordinates of each target
- Transforming image coordinates into physical workspace coordinates
- Passing a selected target to the robot control system

A low-cost fixed-focus webcam such as the Logitech C270 is being considered for the physical system. The final choice depends on field of view, mounting height, image quality, calibration accuracy, and lighting conditions.

### Coordinate Conversion

Object detection initially produces pixel coordinates in the camera image. These cannot be sent directly to the arm. The camera must first be calibrated so that a detected image point can be mapped to a position in the robot's coordinate frame.

For objects placed on a known flat surface, this can be achieved using a calibrated planar transformation. If object height and full three-dimensional position must also be measured, depth information or an additional estimation method will be required.

## Simulation and Control Software

The project includes a real-time interactive arm simulation written in C++17 using Raylib. The simulation provides a visual representation of all six joints and serves as a controlled environment for developing the robot's motion before operating the physical hardware.

The simulation can be used to explore:

- Individual joint movement
- Link geometry and coordinate frames
- Joint-angle limits
- Forward kinematics
- Inverse kinematics
- Reachability of target positions
- Motion sequencing
- Workspace and collision constraints

Separating the simulation from the physical arm makes it possible to validate joint commands and motion logic without immediately risking damage to the mechanism.

### Kinematics

**Forward kinematics** calculates the end-effector pose produced by a known set of six joint angles. It is useful for displaying the arm, checking its position, and validating feedback from the physical joints.

**Inverse kinematics** performs the opposite calculation: given a desired end-effector position and orientation, it determines a valid set of joint angles. A target may have multiple solutions or no reachable solution, so the controller must also consider joint limits, collisions, and the current arm configuration.

## Electronics and Communication

The proposed electronics architecture uses a host computer for high-level vision and motion processing, with a microcontroller handling low-level hardware communication.

The main elements are:

- A host computer running the camera and control software
- An Arduino Uno or equivalent microcontroller
- A TTL serial-bus adapter between the controller and the smart servos
- Six daisy-chained serial-bus servos
- A regulated power supply sized for the motors and pumps
- Two MOSFET switching circuits for the vacuum system
- A separately connected USB camera

The communication path is intended to follow this structure:

```text
Camera -> Vision software -> Target coordinates -> Kinematics and motion control
       -> Microcontroller -> TTL serial bus -> Six joint servos

Motion control -> MOSFET switches -> Vacuum and release pumps
```

The servo power supply must not be sized from nominal current alone. Startup, stall, and simultaneous joint loads must be considered, along with suitable wiring, grounding, protection, and an emergency stop strategy.

## Mechanical Design

The arm proportions are based on ratios taken from the KUKA KR 3 R540 and scaled toward an overall size of approximately 500 mm. Early reference dimensions are:

| Dimension | Approximate target |
| --- | ---: |
| Base height | 195 mm |
| Elbow offset | 25 mm |
| Upper arm | 150 mm |
| Forearm | 150 mm |
| Wrist and flange section | 110 mm |

These values describe the starting geometry rather than fixed manufacturing dimensions. The final design must also account for servo packaging, link stiffness, wiring routes, joint clearance, centre of mass, payload, and the reachable workspace.

## Operating Sequence

A complete automated cycle is intended to work as follows:

1. The camera captures the workspace.
2. The vision system detects and selects a target object.
3. Camera calibration converts the detection into robot coordinates.
4. The controller checks that the target lies inside the safe workspace.
5. Inverse kinematics produces a valid set of joint angles.
6. A motion trajectory moves the arm to an approach pose.
7. The arm lowers the suction cup onto the object.
8. The vacuum pump activates and the object is lifted.
9. The arm follows a safe path to the placement position.
10. The vacuum is released and the second pump separates the object from the cup.
11. The arm returns to a safe resting pose or begins another cycle.

## Design Considerations

The completed system must account for more than simply reaching the target. Important engineering considerations include:

- Joint torque under static and dynamic loading
- Payload capacity and structural deflection
- Position accuracy and repeatability
- Joint limits, singularities, and unreachable poses
- Self-collision and workspace obstacles
- Camera distortion, lighting, and calibration error
- Suction loss and unsuitable object surfaces
- Servo communication or feedback failure
- Power distribution, overcurrent protection, and heat
- Safe startup, shutdown, and emergency stopping

## Technology

| Area | Technology |
| --- | --- |
| Interactive simulation | C++17, Raylib |
| Camera and computer vision | Python, OpenCV |
| Embedded control | Arduino-compatible controller |
| Joint communication | TTL serial bus |
| Actuation | Smart servos with encoder feedback |
| End effector | Dual-pump vacuum system with MOSFET switching |

## Project Journey

The design process, major engineering decisions, test results, problems encountered, and final outcome will be documented here once the main project milestones have been completed. Keeping that retrospective separate from the technical overview allows this README to remain a useful description of the system without requiring constant progress updates.

## Acknowledgements

The arm geometry is inspired by the published proportions of the KUKA KR 3 R540. KUKA and KR 3 are trademarks of their respective owner. This repository is an independent student engineering project.

## License

MIT LICENSE