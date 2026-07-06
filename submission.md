# Omokai Robotics Engineering Task - Submission Report

## 1. Project Overview

This project implements a simple AI-assisted robot patrol system using ROS 2 and Google Gemini.

The user provides a natural language command, which is converted into a structured JSON mission using the Gemini API. The JSON mission is then executed by a ROS 2 node that controls the robot while using LiDAR data for obstacle avoidance.

The LLM is only responsible for understanding the user's instruction. All robot movement and obstacle avoidance are handled by deterministic ROS 2 code.

---

## 2. System Architecture

The system follows this pipeline:

User Prompt
→ Gemini LLM
→ JSON Mission
→ Mission Validation
→ Robot Executor
→ Robot Motion in Simulation

### Components

### llm_parser.py

- Accepts a natural language command.
- Uses Gemini 2.5 Flash to generate a structured JSON response.
- Returns only JSON.

Example:

```json
{
  "mission": "patrol",
  "loops": 1,
  "distance": 5,
  "speed": 0.2,
  "return_home": false
}
```

### validator.py

Checks that the generated mission is valid before execution.

This prevents invalid or missing mission parameters from reaching the robot controller.

### executor.py

Implements the ROS 2 control node.

Responsibilities include:

- Reading LiDAR data
- Detecting nearby obstacles
- Slowing down near obstacles
- Steering around obstacles
- Tracking travelled distance
- Stopping after the requested distance

---

## 3. Obstacle Avoidance

The robot continuously monitors LaserScan data.

The LiDAR scan is divided into regions:

- Front
- Front-left
- Front-right
- Rear

The controller behaves as follows:

- If the path is clear, move forward.
- If an obstacle is nearby, reduce speed.
- If the obstacle is too close, steer toward the side with more free space.
- If the robot is trapped, reverse briefly before turning.

This allows the robot to patrol while avoiding collisions without requiring hardcoded paths.

---

## 4. Design Decisions

The project separates high-level planning from low-level control.

The LLM is used only once to convert the user's instruction into a structured mission.

All robot control decisions are performed locally using deterministic ROS 2 logic and live sensor data.

This keeps the control loop predictable and safe.


---

## 5. Sources

- ROS 2 Humble Documentation - Documentation: https://docs.ros.org/en/humble/

- TurtleBot3 Simulation Packages
- Google Gemini API Documentation

These resources were used as references while developing the project.
