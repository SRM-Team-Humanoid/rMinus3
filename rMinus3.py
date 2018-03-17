#!/usr/bin/env python
import rospy
import time
import yaml
import numpy as np
import anglereader

import pprint


ANGLES_DB_PATH = "angles.json"

class Robot(object):
    """Main Class that is used to define  Robot behaviour """


    def __init__(self,motor_ids,motion_script="",control="FRAME"):
    
        #Initialize Ids

        if type(motor_ids) == int:
            self.ids = [x for x in range(1,motor_ids+1)]
        elif type(motor_ids) == list:
            self.ids = motor_ids
        else:
            print "ERROR: Motor IDs must be specified as a list or an integer"
            exit()

        
        
        #Initialize Robot Internal State
        self.state = dict.fromkeys(self.ids,0.0)
        self.primitives = {}
        self.control = control
        
        #Load Primitives
        try:
            with open(motion_script,"r") as file:
                motion_data = yaml.load(file)
                
            for prim in motion_data:
                self.primitives[prim] = self.load_primitive(motion_data[prim])
                

        except Exception as e:
            print "Error Parsing File"
            print e
            exit()



    def load_primitive(self,prim_dict):
        
        reader = anglereader.AngleReader(ANGLES_DB_PATH)
        
        primitive_angles = []
        last_frame = 0
        frame_counter = 0

        for motion in prim_dict:
            if motion["Type"] == "Page":
                angles = reader.parse(motion["Code"])
                for angle in angles:
                    angle = list(angle)
                    angle[0] += frame_counter
                    angle[1] = self.set_speed(angle[1],motion["Speed"])
                    primitive_angles.append(angle)
                    last_frame = angle[0]
                frame_counter = last_frame + 1
            elif motion["Type"] == "Flow":
                angleset = reader.setparse(motion["Code"])
                for angles in angleset:
                    for angle in angles:
                        angle = list(angle)
                        angle[0] += frame_counter
                        angle[1] = self.set_speed(angle[1],motion["Speed"])
                        primitive_angles.append(angle)
                        last_frame = angle[0]
                    frame_counter = last_frame + 1


            else:
                raise ValueError( "ERROR : Type must be Page/Flow")


        return primitive_angles




    def set_speed(self,val,modifier):
        """Modify Speed Value according to the modifier provided"""

        if modifier[0] == "x":
            return val*float(modifier[1:])
        elif modifier[0] == "a":
            return float(modifier[1:])
        else:
            raise ValueError("Speed Modifier must start with x/a")



    def execute(self,primitive):
        if self.control == "FRAME":
            self.frame_compute(primitive)
        elif self.control == "SPEED":
            self.speed_compute(primitive)



    def frame_compute(self,primitive):
        pass

    def speed_compute(self,primitive):
        pass





r = Robot(6,"motion_script.yaml")
r.execute("Left")
