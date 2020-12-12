from hitobjects import *
import re
import copy

class TimingPoint:
    Inherited = 0
    Uninherited = 1
    
class Event:
    def __init__(eventType=str(), startTime=int()):
        self.eventType = eventType
        self.startTime = startTime

class Background(Event):
    def __init__(eventType=str(), startTime=int(), filename=str(), xOffset=int(), yOffset=int()):
        super().__init__(eventType, startTime)
        self.filename = filename
        self.xOffset = xOffset
        self.yOffset = yOffset

class Video(Event):
    def __init__(eventType=str(), startTime=int(), filename=str(), xOffset=int(), yOffset=int()):
        super().__init__(eventType, startTime)
        self.filename = filename
        self.xOffset = xOffset
        self.yOffset = yOffset

class Break(Event):
    def __init__(eventType=str(), startTime=int(), endTime=int()):
        super().__init__(eventType, startTime):
        self.endTime = endTime

class Beatmap:
    def __init__(self, fullpath=None):
        self.formatVersion = None
        self.general = dict()
        self.editor = dict()
        self.metadata = dict()
        self.difficulty = dict()
        self.events = list()
        self.timingPoints = list()
        self.colours = dict()
        self.hitObjects = list()
        
        with open(fullpath, encoding="utf8") as file:
            lines = file.readlines()
            
            self._section = -1

            for line in lines:
                self.parseLine(line.replace("\n", ""))
        
    def getTimingPoint(self, time, uninherited):
        r = None
        
        for tp in self.timingPoints:
            if tp.time <= time:
                if tp.uninherited == uninherited:
                    r = point
            else:
                break

        return r
        
    def parseLine(self, line, section):
        if len(line) < 1 or line == "\n":
            return
        
        if line.startswith("["):
            if line == "[General]": 
                self.section = 0
            elif line == "[Editor]": 
                self.section = 1
            elif line == "[Metadata]": 
                self.section = 2
            elif line == "[Difficulty]": 
                self.section = 3
            elif line == "[Events]": 
                self.section = 4
            elif line == "[TimingPoints]": 
                self.section = 5
            elif line == "[Colours]": 
                self.section = 6
            elif line == "[HitObjects]": 
                self.section = 7
            else: 
                self.section =  -1
        
        if self.section == 0: 
            self.parseGeneral(line)
        elif self.section == 1: 
            self.parseEditor(line)
        elif self.section == 2: 
            self.parseMetadata(line)
        elif self.section == 3: 
            self.parseDifficulty(line)
        elif self.section == 4: 
            self.parseEvents(line)
        elif self.section == 5: 
            self.parseTimingPoints(line)
        elif self.section == 6: 
            self.parseColors(line)
        elif self.section == 7: 
            self.parseHitObjects(line)
        else:
            return
        
    def parseGeneral(self, line):
        line = line.split(":")

        if line[0] == "AudioFilename":
            self.general[line[0]] = line[1]
        elif line[0] == "SampleSet":
            self.general[line[0]] = line[1]
        elif line[0] == "StackLeniency":
            self.general[line[0]] = float(line[1])
        else:
            self.general[line[0]] = int(line[1])
            
    def parseEditor(self, line):
        line = line.split(":")
        
        if line[0] == "Bookmarks":
            self.editor[line[0]] = line[1].split(",")
        elif line[0] == "DistanceSpacing":
            self.editor[line[0]] = float(line[1])
        elif line[0] == "TimelineZoom":
            self.editor[line[0]] = float(line[1])
        else:
            self.editor[line[0]] = int(line[1]) 

    def parseMetadata(self, line):
        line = line.split(":")

        if len(line) > 2:
            self.metadata[line[0]] = "".join(line)

        if line[0] == "Tags":
            self.metadata[line[0]] = line[1].split(" ")
        elif line[0] == "BeatmapID":
            self.metadata[line[0]] = int(line[1])
        elif line[0] == "BeatmapSetID":
            self.metadata[line[0]] = int(line[1])
        else:  
            self.metadata[line[0]] = line[1]
        
    def parseDifficulty(self, line):
        line = line.split(":")
        self.difficulty[line[0]] = float(line[1])

    def parseEvents(self, line):
        self.events.append(line)

    def parseTimingPoints(self, line):
        line = line.split(",")

        tp = TimingPoint()
        tp.time = int(line[0])
        tp.beatLength = float(line[1]),
        tp.meter = int(line[2]),
        tp.sampleSet = int(line[3]),
        tp.sampleIndex = int(line[4]),
        tp.volume = int(line[5]),
        tp.uninherited = bool(int(line[6]))
        tp.effects = int(line[7])
        
        self.timingPoints.append(tp)

    def parseColours(self, line):
        line = line.split(":")
        self.colours[line[0]] = line[1]
        
    def parseHitObjects(self, line):

        line = line.split(",")

        x = int(line[0]) 
        y = int(line[1]) 
        time = int(line[2])
        type_ = int(line[3]) 
        hitSound = int(line[4])  

        # Circle
        if 1 & int(type_): 
            hitObject = Circle(x, y, time, type_, hitSound)
            hitObject.hitSample = int(line[5])

        # Slider      
        if 2 & int(type_):
            hitObject = Slider(x, y, time, type_, hitSound)
            
            l = line[5].split("|")
            hitObject.curveType = l[0]

            for i in range(1, len(l)):
                coords = l[i].split(":")
                hitObject.curvePoints.append(Point(int(coords[0]), int(coords[1])))
                        
            hitObject.slides = int(line[6])
            hitObject.length = float(line[7])

        # Spinner 
        if 8 & int(type_):         
            hitObject = Spinner(x, y, time, type_, hitSound)
            hitObject.endTime = int(line[5])
            hitObject.hitSample = int(line[6])

        
        self.hitObjects.append(hitObject)


    def replaceHitObject(self, hitobject):
        for h in self.hitObjects:
            if h.time == h.time:
                h = hitobject
                return True
        return False
            
    def addTimingPoint(self, timingPoint):
        for i, tp in enumerate(self.timingPoints):
            if tp.time == timingPoint.time and tp.uninherited == timingPoint.uninherited:
                tp = timingPoint
                return
            
            elif tp.time > timingPoint.time:
                self.timingPoints.insert(i, timingPoint)
                return

    # Writing to file and naming it properly
    def write_beatmap(beatmap, file):
        file.write(self.formatVersion + "\n\n")
        
        # [General]
        file.write(("[General]\n")
        for k, v in self.general.items():
            file.write(k + ":" + str(v) + "\n")
        file.write("\n")


        # [Editor]
        file.write("[Editor]\n")
        for k, v in self.editor.items():
            if k == "Bookmarks":
                file.write(k + ":" + "".join(v) + "\n")
            else:
                file.write(k + ":" + str(v) + "\n")
        file.write("\n")

        # [Metadata] section
        file.write("[Metadata]\n")
        for k, v in self.metadata.items():
            if k == "Tags":
                file.write(k + ":" + " ".join(v) + "\n")
            else:
                file.write(k + ":" + str(v) + "\n")
        file.write("\n")

        # [Difficulty] section
        file.write("[Diffculty]\n")
        for k, v in self.difficulty.items():
            file.write(k + ":" + str(v) + "\n")
        file.write("\n")

        # [Events] section
        file.write("[Events]\n")
        for i in self.events:
            file.write(i + "\n")
        file.write("\n")

        # [TimingPoints] section
        file.write("[TimingPoints]\n")
        for i in self.timing_points:
            file.write(str(i.time) + ",") 

            if i.type == 1:
                file.write(str(i.beatLength) + ",")
            else:
                file.write(str(-100 / i.beatLength) + ",")

            file.write(str(i.meter) + ","
                     + str(i.sampleSet) + "," 
                     + str(i.sampleIndex) + "," 
                     + str(i.volume) + "," 
                     + str(i.type) + "," 
                     + str(i.effect) + "\n")

        file.write("\n")

        # [Colours] section
        if self.colours:
            file.write("[Colours]\n")
            for k, v in self.colours.items():
                file.write(k + ":" + v + "\n")
            file.write("\n")

        # [Hitobjects] section
        file.write("[Hitobjects]\n")
        for i in self.hitobjects:
            file.write(str(i.x) + "," 
                     + str(i.y) + "," 
                     + str(i.time) + "," 
                     + str(i.type) + "," 
                     + str(i.hitsound) + ",")
            
            # Circle
            if i.type & HitObject.Circle:
                file.write(str(i.hitsample) + "\n")
                
            # Slider
            if i.type & HitObject.Slider:
                file.write(str(i.curveType))
                for j in i.curvePoints:
                    file.write("|" + str(int(j.x)) + ":" + str(int(j.y)))
                file.write("," + str(i.slides) + "," + str(i.length) + "\n")

            # Spinner
            if i.type & HitObject.Spinner:
                file.write(str(endtime) + str(hitsample) + "\n")

        file.write("\n")
    
        

