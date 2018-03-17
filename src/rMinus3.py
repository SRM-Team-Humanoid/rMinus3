#!/usr/bin/env python
import rospy
import os
import subprocess
import time
import yaml
import numpy as np
import anglereader



#Set Current Working Directory
path = subprocess.check_output("rospack find rMinus3",shell=True) 
path = path[:-1]+"/src"
os.chdir(path)




ANGLES_DB_PATH = "angles.json"
DEFAULT_SPEED = 200
TIME_CONST = 0.008


darwin = {1: 90, 2: -90, 3: 67.5, 4: -67.5, 7: 45, 8: -45, 9: 'i', 10: 'i', 13: 'i', 14: 'i', 17: 'i', 18: 'i'}

PROCESS_PIPELINE = [darwin]

class Robot(object):
    """Main Class that is used to define  Robot behaviour """


    def __init__(self,motor_ids,motion_script="",control="FRAME",speed=DEFAULT_SPEED):
    
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
        self.speed = speed


        #Load Primitives from Motion Script
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
        """Merges Pages and Flows together so that a primitive is simply a set
        of motions, where each motion consists of a frame, speed, dict of
        angles """
        
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
        """Calls corresponding compute function based on control mode"""

        if self.control == "FRAME":
            self.frame_compute(primitive)
        elif self.control == "SPEED":
            self.speed_compute(primitive)



    def frame_compute(self,primitive):
        """Creates Intermediate Frames between each frame which are to be
        executed sequentially. Motor Speed is constant"""

        motion_set = []
        init = [0,1,self.state.values()]
        motion_set.append(init)


        for prim in self.primitives[primitive]:
            prim = [prim[0],prim[1],self.process_motion(prim[2])]
            motion_set.append(prim)





        for m in motion_set:
            print m

    def speed_compute(self,primitive):
        #TODO

        pass


    
    def process_motion(self,motion):
        """Processes each motion_dict to apply offsets/modifiers specified in
        PROCESS_PIPELINE"""

        motion = {id:motion[id] for id in self.ids}
        
         
        for process in PROCESS_PIPELINE:
            for id in self.ids:
                if id in process:
                    val = process[id]
                    if val == "i":
                        motion[id] = -1 * motion[id]
                    else:
                        motion[id] += val

                    motion[id] = round(motion[id],2)
        
        return motion


r = Robot(9,"motion_script.yaml")
r.execute("Dummy")
