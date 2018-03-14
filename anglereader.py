import json


class AngleReader(object) :
    def __init__(self,file) :
        try :
            with open(file,"r") as f :
	        self.data = json.load(f)
	except :
	    raise RuntimeError("File not found")


		
    def parse(self,motion) :
        motions = []
	frames = []
	js = self.data["Root"]["PageRoot"]["Page"]
	for j in js :
	    try :	
	        if motion in j["name"]:
	            for step in j["steps"]["step"] :
                        motion_str = step["pose"]
                        motion_list = [float(m) for m in motion_str.split()]
		        motions.append(motion_list)
			frames.append(int(step["frame"]))
					
	    except Exception as e:
		raise RuntimeError(e)
		
		
        return zip(frames,motions)
			
    def setparse(self,motion,offset=[]) :
        js = self.data["Root"]["FlowRoot"]["Flow"]
        motionset = []
        for j in js :
            try : 
                if motion in j["name"] :
                    for unit in j["units"]["unit"] :
                        motionset.append(self.parse(motion=unit["main"]))
            except Exception as e:
                raise RuntimeError(e)

        return motionset



