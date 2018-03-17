import json


class AngleReader(object) :
    def __init__(self,file) :
        try :
            with open(file,"r") as f :
	        self.data = json.load(f)
	except :
	    raise RuntimeError("File not found")


		
    def parse(self,motion,speed=1) :
        motions = []
	frames = []
        ids = [x for x in range(1,19)]
	js = self.data["Root"]["PageRoot"]["Page"]
	for j in js :
	    try :	
	        if motion == j["name"]:
	            for step in j["steps"]["step"] :
                        motion_str = step["pose"]
                        motion_list = [float(m) for m in motion_str.split()]
                        motion_list = dict(zip(ids,motion_list))
		        motions.append(motion_list)
			frames.append(int(step["frame"]))
					
	    except Exception as e:
		raise RuntimeError(e)
		
	
        speeds = [float(speed) for x in frames]
        return list(zip(frames,speeds,motions))
			
    def setparse(self,motion,offset=[]) :
        js = self.data["Root"]["FlowRoot"]["Flow"]
        motionset = []
        for j in js :
            try : 
                if motion == j["name"] :
                    for unit in j["units"]["unit"] :
                        motionset.append(self.parse(motion=unit["main"],speed=unit["mainSpeed"]))
            except Exception as e:
                raise RuntimeError(e)

        return motionset



