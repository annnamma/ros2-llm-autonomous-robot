# Omokai Robotics Engineering Task

## Overview

This project implements a natural language controlled autonomous robot using ROS2 and Google Gemini.

The user provides a command such as:

> Patrol 5 meters at 0.15 m/s

The system converts the prompt into a structured JSON mission using Gemini, validates the mission parameters, and executes it using a deterministic ROS2 controller with LiDAR-based obstacle avoidance.

---

## System Architecture

Natural Language Prompt
        │
        ▼
Gemini LLM
        │
        ▼
Mission JSON
        │
        ▼
Mission Validator
        │
        ▼
ROS2 Robot Executor
        │
        ▼
LiDAR Feedback
        │
        ▼
Obstacle Avoidance
        │
        ▼
TurtleBot3 Simulation

---

## Features

- Natural language robot commands
- Gemini-powered prompt parsing
- JSON validation
- Deterministic robot controller
- Continuous LiDAR obstacle avoidance
- Distance-based mission completion
- ROS2 Humble compatible

---

## Project Structure

```
robot/
│
├── executor.py
├── llm_parser.py
├── validator.py
└── ...
```

---

## Requirements

- Ubuntu 22.04
- ROS2 Humble
- TurtleBot3 Simulation
- Python 3.10
- Google Gemini API Key

---

## Installation

Clone the workspace and build.



Before running the project, set your Gemini API key.

```bash
export GEMINI_API_KEY=YOUR_API_KEY
```

Then run:

```bash
ros2 run robot executor
```
```bash
cd ~/ros2_ws

source /opt/ros/humble/setup.bash

colcon build

source install/setup.bash
```

---

## Run

Launch Gazebo.

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Run the executor.

```bash
ros2 run robot executor
```

Example prompt:

```
Patrol 5 meters at 0.15 m/s
```

---

## Example Output

```
Generated JSON:

{
    "mission":"patrol",
    "distance":5,
    "speed":0.15,
    "loops":1
}

Mission Valid

Beginning Exploration...
Obstacle detected
Turning Left
Mission Complete
```

--
