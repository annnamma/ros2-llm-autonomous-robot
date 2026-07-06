FROM osrf/ros:humble-desktop-full

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-simulations \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    google-generativeai

# TurtleBot3 model
ENV TURTLEBOT3_MODEL=burger

# Workspace
WORKDIR /ros2_ws

# Copy workspace
COPY . .

# Build package
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

# Automatically source ROS
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["/bin/bash"]
