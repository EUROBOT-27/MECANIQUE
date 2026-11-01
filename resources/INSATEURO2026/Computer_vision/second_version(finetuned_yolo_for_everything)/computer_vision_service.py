#!/usr/bin/env python3
import rospy
from std_srvs.srv import Trigger, TriggerResponse

# Import all task functions
from task1_color_detection.color_detection_ver1 import detect_color_from_camera
from second_task_number_detection.yolo_only import detect_number_from_camera
from task3_object_detection.last_version.yolo_minimal import detect_object_from_camera

def handle_service1(req):
    color = detect_color_from_camera(show_window=False)
    if color:
        return TriggerResponse(success=True, message=color)
    else:
        return TriggerResponse(success=False, message="No color detected")

def handle_service2(req):
    number = detect_number_from_camera(show_window=False)
    if number:
        return TriggerResponse(success=True, message=number)
    else:
        return TriggerResponse(success=False, message="No number detected")

def handle_service3(req):
    obj = detect_object_from_camera(show_window=False)
    if obj:
        return TriggerResponse(success=True, message=obj)
    else:
        return TriggerResponse(success=False, message="No object detected")

def computer_vision_service():
    rospy.init_node('computer_vision_service')
    s1 = rospy.Service('service1', Trigger, handle_service1)
    s2 = rospy.Service('service2', Trigger, handle_service2)
    s3 = rospy.Service('service3', Trigger, handle_service3)
    rospy.loginfo("Computer Vision Service Ready: service1 (color), service2 (number), service3 (object)")
    rospy.spin()

if __name__ == "__main__":
    computer_vision_service()
