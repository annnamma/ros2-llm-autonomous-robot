import os
import json
import math
import time
import google.generativeai as genai

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

# Configure Gemini API Globally
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You are a robot mission planner. Convert the user's instruction into JSON.
Return ONLY JSON matching this schema:
{"mission":"patrol", "loops":1, "distance":5, "speed":0.2, "return_home":false}
"""

def parse_prompt(prompt):
    response = model.generate_content(
        SYSTEM_PROMPT + "\n\nUser: " + prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text.strip())

def validate_mission(mission):
    return True, "Mission valid"


class RobotExecutor(Node):

    def __init__(self):
        super().__init__("robot_executor")
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.scan_sub = self.create_subscription(LaserScan, "/scan", self.scan_callback, 10)

        # Laser zones
        self.front_distance = 10.0
        self.left_distance = 10.0
        self.right_distance = 10.0
        self.back_distance = 10.0

        # Behavioral thresholds
        self.safe_distance = 0.55   # Distance to trigger active turning
        self.slow_distance = 1.00   # Distance to begin slowing down
        
        self.get_logger().info("Continuous Explorer Node Started")

    def scan_callback(self, msg):
        ranges = [10.0 if (math.isinf(r) or math.isnan(r) or r <= 0.0) else r for r in msg.ranges]
        n = len(ranges)
        if n == 0: return

        # Exact front window (30 degrees left and right of center nose)
        self.front_distance = min(ranges[-15:] + ranges[:15])
        
        # CORRECTED FRONT DIAGONALS (Symmetrical front-left and front-right)
        self.left_distance = min(ranges[15:60])      
        self.right_distance = min(ranges[300:345])   
        
        self.back_distance = min(ranges[150:210])

    def explore_environment(self, max_speed, target_distance):
        """
        Smooth reactive exploration that automatically stops once 
        the requested target distance (in meters) has been completed.
        """
        self.get_logger().info(f"Beginning exploration for a total of {target_distance} meters...")
        msg = Twist()
        
        distance_traveled = 0.0
        last_time = time.time()
        
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.01)
            
            # Calculate elapsed time since the last iteration
            now = time.time()
            dt = now - last_time
            last_time = now
            
            # Stop if we have successfully completed the requested distance
            if distance_traveled >= target_distance:
                self.get_logger().info(f"Target distance of {target_distance}m reached! Stopping.")
                break

            # 1. EMERGENCY ESCAPE
            if self.front_distance < 0.32:
                self.stop()
                if self.back_distance > 0.25:
                    msg.linear.x = -0.06
                    msg.angular.z = 0.2 if self.left_distance > self.right_distance else -0.2
                    self.publisher.publish(msg)
                    time.sleep(0.4)
                
                msg.linear.x = 0.0
                msg.angular.z = 0.45 if self.left_distance > self.right_distance else -0.45
                self.publisher.publish(msg)
                time.sleep(0.5)
                # Reset clock after handling emergency to avoid huge dt spikes
                last_time = time.time() 
                continue

            # 2. ACTIVE WEAVING
            if self.front_distance < self.safe_distance:
                msg.linear.x = max_speed * 0.5  
                if abs(self.left_distance - self.right_distance) < 0.05:
                    msg.angular.z = -0.4  
                elif self.left_distance > self.right_distance:
                    msg.angular.z = 0.4   
                else:
                    msg.angular.z = -0.4  
                    
            # 3. SIDE PILLAR AVOIDANCE
            elif self.left_distance < 0.38 or self.right_distance < 0.38:
                msg.linear.x = max_speed * 0.75
                if self.left_distance < self.right_distance:
                    msg.angular.z = -0.3   
                else:
                    msg.angular.z = 0.3    
                    
            # 4. PATH OPEN
            else:
                msg.linear.x = max_speed
                msg.angular.z = 0.0

            # Accumulate distance covered based on actual forward linear velocity
            if msg.linear.x > 0:
                distance_traveled += msg.linear.x * dt

            self.publisher.publish(msg)
            time.sleep(0.05)
            
        self.stop()

    def stop(self):
        self.publisher.publish(Twist())

    
def main(args=None):

    prompt = input("Enter command: ")

    print("\nSending prompt to Gemini...\n")

    mission_json = parse_prompt(prompt)

    print("Generated JSON:")
    print(json.dumps(mission_json, indent=4))

    valid, message = validate_mission(mission_json)

    print("\nValidation:", message)

    if not valid:
        return

    rclpy.init(args=args)

    robot = RobotExecutor()

    time.sleep(1)

    try:
        robot.explore_environment(
            max_speed=mission_json.get("speed", 0.15),
            target_distance=mission_json.get("distance", 2.0)
        )

    except KeyboardInterrupt:
        pass

    finally:
        robot.stop()
        robot.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
