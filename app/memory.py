import json,time
from collections import defaultdict,deque
class SevenLayerMemory:
    """Local runnable reference. Production adapters can map layers to Redis/Postgres/vector/Foundry Memory."""
    def __init__(self):
        self.working=defaultdict(dict)
        self.conversation=defaultdict(lambda: deque(maxlen=50))
        self.episodic=defaultdict(list)
        self.semantic=defaultdict(list)
        self.procedural=defaultdict(dict)
        self.entity=defaultdict(dict)
        self.audit=defaultdict(list)
    def put(self,tenant,layer,key,value):
        rec={"key":key,"value":value,"ts":time.time()}
        if layer=="working": self.working[tenant][key]=rec
        elif layer=="conversation": self.conversation[tenant].append(rec)
        elif layer=="episodic": self.episodic[tenant].append(rec)
        elif layer=="semantic": self.semantic[tenant].append(rec)
        elif layer=="procedural": self.procedural[tenant][key]=rec
        elif layer=="entity": self.entity[tenant][key]=rec
        elif layer=="audit": self.audit[tenant].append(rec)
        else: raise ValueError("unknown memory layer")
        return rec
    def snapshot(self,tenant):
        return {
          "working":list(self.working[tenant].values()),
          "conversation":list(self.conversation[tenant]),
          "episodic":self.episodic[tenant][-20:],
          "semantic":self.semantic[tenant][-20:],
          "procedural":list(self.procedural[tenant].values()),
          "entity":list(self.entity[tenant].values()),
          "audit":self.audit[tenant][-20:]
        }
memory=SevenLayerMemory()
