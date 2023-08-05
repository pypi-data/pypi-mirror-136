# Basic Robotics

Basic Robotics is divided into several different component libraries:
 - basic_robotics.general - Basic robotics math, transforms, helper functions")
 - basic_robotics.interfaces - Hardware communications skeletons for physical robots")
 - basic_robotics.kinematics - Serial and Parallel robot kinematics classes")
 - basic_robotics.modern_robotics_numba - Numba enabled version of NxRLab's Modern Robotics")
 - basic_robotics.path_planning - RRT* path planning variations and spatial indexing")
 - basic_robotics.plotting - Simple Plotting functions for visualizations of robots")
 - basic_robotics.robot_collisions - Fast Collision Manager for robotics and obstacles
 - basic_robotics.utilities - Terminal Displays and Logging

## General Functionality
FASER Interfaces is a general toolkit for functions used elswehere in other related repositories, and feautres tm: a transformation library, FASER: a catchall repository for useful functions, and Faser High Performance, an extension of [Modern Robotics](http://hades.mech.northwestern.edu/index.php/Modern_Robotics)'s robotics toolkit.
### Features
#### TM Library
- Abstracted handling and display of transformation matrices.
- Fully overloaded operators for addition, multiplication, etc
- Generate transforms from a variety of input types
- Easily extract positions and rotations in a variety of formats

#### FASER High Performance
- Provides kinematic extensions to the faser_robotics_kinematics library
- Accelerated with Numba, and extends [Modern Robotics](http://hades.mech.northwestern.edu/index.php/Modern_Robotics).

#### FASER (fsr)
- Catchall functions for manipulation of data elsewhere in FASER system
- Simple trajectory generation
- Position interpolation

### Usage
Usage Examples:

```python
# Start with the transformation library
import numpy as np
from basic_robotics.general import tm

# Import the disp library to properly view instances of the transformations
from basic_robotics.utilities.disp import disp

#The transformation library allows for seamless usage of rotation matrices and other forms of rotation information encoding.
identity_matrix = tm()
disp(identity_matrix, 'identity') #This is just zeros in TAA format.

#Let's create a few more.
trans_x_2m = tm([2, 0, 0, 0, 0, 0]) #Translations can be created with a list (Xm, Ym, Zm, Xrad, Yrad, Zrad)
trans_y_4m = tm(np.array([0, 4, 0, 0, 0, 0])) # Translations can be created with a numpy array
rot_z_90 = tm([0, 0, 0, 0, 0, np.pi/2]) # Rotations can be declared in radians
trans_z_2m_neg = tm(np.array([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, -2], [0, 0, 0, 1]]))
# Transformations can be created from rotation matrices

trans_x_2m_quat = tm([2, 0, 0, 0, 0, 0, 0]) # Transformations can even be declared with quaternions

list_of_transforms = [trans_x_2m, trans_y_4m, rot_z_90]
disp(list_of_transforms, 'transform list') # List of transforms will be displayed in columns

#Operations
new_simple_transform = trans_x_2m + trans_y_2m #Additon is element-wise on TAA form
new_transform_multiplied = trans_x_2m @ trans_y_2m #Transformation matrix multiplication uses '@'
new_double_transform = trans_x_2m * 2 # Multiplication by a scalar is elementwise

#And more visible in the documentation


```
Detailed Usage TODO

## Interfaces
FASER Interfaces is a simple toolkit for communicating over serial and udp through a common interface, and used generally to communicate with robots or sensors

### Features
- Generalized "Comms" implementation
- Communications supervisor
- Standard interface for Serial and UDP


### Usage

Detailed Usage TODO

## Kinematics
FASER Robotics Kinematics is a toolbox for kinematics, statics, and dynamics of Stewart Platforms and Serial Manipulators, largely based on [Modern Robotics](http://hades.mech.northwestern.edu/index.php/Modern_Robotics). It is part of a set of related robotics repositories hosted here.

### Features

#### Stewart Platforms:
- Forward and Inverse Kinematics
- Static Analysis and Force Calculations
- Custom Configurations
- Error detection and correction

#### Serial Manipulators:
- Forward and Inverse Kinematics
- Static Analysis and Force Calculations
- Custom Configurations
- Error detection and correction
- Dynamics Analysis
- Visual Servoing and Path Planning

### Usage

Detailed Usage TODO

## Modern Robotics - Numba
TODO Explanation
This repository contains the code library accompanying [_Modern Robotics:
Mechanics, Planning, and Control_](http://modernrobotics.org) (Kevin Lynch
and Frank Park, Cambridge University Press 2017). The
[user manual](/doc/MRlib.pdf) is in the doc directory.

The functions are available in:

* Python
* MATLAB
* Mathematica

Each function has a commented section above it explaining the inputs required for its use as well as an example of how it can be used and what the output will be. This repository also contains a pdf document that provides an overview of the available functions using MATLAB syntax. Functions are organized according to the chapter in which they are introduced in the book. Basic functions, such as functions to calculate the magnitude of a vector, normalize a vector, test if the value is near zero, and perform matrix operations such as multiplication and inverses, are not documented here.

The primary purpose of the provided software is to be easy to read and educational, reinforcing the concepts in the book. The code is optimized neither for efficiency nor robustness.

## Path Planning
FASER Path planning is a toolbox for using RRT* to plan paths quickly through adverse terrain in a generalized sense (compatible with a wide variety of robotic tools)
### Features
- RRT* generation for various configurations
- Fake terrain generation
- Collision detection and obstacle avoidance
- Bindable functions for advanced tuning
- Dual Path RRT* for quicker solution finding
### Usage

Detailed Usage TODO

## Plotting
FASER Plotting is a simple toolbox which extends matplotlib to draw simple shapes and show how a robot fits together.
### Features
- Animate videos using matplotlib frames
- Plot various primary shapes
- Plot FASER Robots
- Plot transforms and wrenches
### Usage

Detailed Usage TODO

## Robot Collisions
TODO

## Utilities
Utilities contains display and logging tools generally useful for working with other components in this package
### Features
- matlab like display function 'disp' which is a drop in replacement for python print()
- JSON file logging tool
- Print matrices with appropriate labels
- ProgressBar display
### Usage
Detailed Usage TODO
