from hitobjects import *
from utils import Point, fileToSvm, getUninheritedPoint, getInheritedPoint


class Beatmap:
    def __init__(self, fullpath):
        self.hitTimeWindows = dict()
        self.circleRadius = 0

        self.general = dict()
        self.editor = dict()
        self.metadata = dict()
        self.difficulty = dict()
        self.events = list()
        self.timingPoints = list()
        self.colours = dict()
        self.hitobjects = list()
        self.section = -1

        try:
            with open(fullpath, encoding="utf8") as file:
                rawLines = file.readlines()

        except IOError:
            print("[ERROR] Beatmap couldn't be opened")

        tmp = fullpath.split("\\")
        if tmp:
            self.path = "".join(tmp[:-1])
            self.filename = "".join(tmp[-1])
        else:
            self.path = str()
            self.filename = fullpath
                
        self.osuFileVersion = rawLines[0].replace("\n", "")
            
        for line in rawLines:
            self.parse_line(line.replace("\n", ""))

        #
        #         |                                              |
        #   miss  |  50  |  100  |  300  I  300  |  100  |  50   |  miss
        #         [______________________________________________]
        #                         Minimal HitTimeWindow
        self.hitTimeWindows["300"] = 79 - (self.difficulty["OverallDifficulty"] * 6)  + 0.5
        self.hitTimeWindows["100"] = 139 - (self.difficulty["OverallDifficulty"] * 8) + 0.5
        self.hitTimeWindows["50"] = 199 - (self.difficulty["OverallDifficulty"] * 10) + 0.5
        self.hitTimeWindows["miss"] = 259 - (self.difficulty["OverallDifficulty"] * 12) + 0.5

        self.circleRadius = (109 - 9 * self.difficulty["CircleSize"]) / 2


        
    def parse_line(self, line):

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
                self.section = -1
            return
        
        if self.section == 0:
            self.handle_general(line)
        elif self.section == 1:
            self.handle_editor(line)
        elif self.section == 2:
            self.handle_metadata(line)
        elif self.section == 3:
            self.handle_difficulty(line)
        elif self.section == 4:
            self.handle_events(line)
        elif self.section == 5:
            self.handle_timingpoint(line)
        elif self.section == 6:
            self.handle_colours(line)
        elif self.section == 7:
            self.handle_hitobject(line)

    def handle_metadata(self, line):
        line = line.split(":")

        # For titles like <Re:Queen'm>, etc.
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
        
    def handle_difficulty(self, line):
        line = line.split(":")
        self.difficulty[line[0]] = float(line[1])

    def handle_colours(self, line):
        line = line.split(":")
        self.colours[line[0]] = line[1]
        
    def handle_general(self, line):
        line = line.split(":")

        if line[0] == "AudioFilename":
            self.general[line[0]] = line[1]
        elif line[0] == "SampleSet":
            self.general[line[0]] = line[1]
        elif line[0] == "StackLeniency":
            self.general[line[0]] = float(line[1])
        else:
            self.general[line[0]] = int(line[1])

    def handle_events(self, line):
        self.events.append(line)
        
    def handle_editor(self, line):
        line = line.split(":")
        
        if line[0] == "Bookmarks":
            self.editor[line[0]] = line[1].split(",")
        elif line[0] == "DistanceSpacing":
            self.editor[line[0]] = float(line[1])
        elif line[0] == "TimelineZoom":
            self.editor[line[0]] = float(line[1])
        else:
            self.editor[line[0]] = int(line[1])
        

    def handle_timingpoint(self, line):
        
        line = line.split(",")

        timingPoint = TimingPoint(int(line[0]),
                                   float(line[1]),
                                   int(line[2]),
                                   int(line[3]),
                                   int(line[4]),
                                   int(line[5]),
                                   int(line[6]),
                                   int(line[7]))
        
        self.timingPoints.append(timingPoint)
        


    def handle_hitobject(self, line):

        line = line.split(",")

        x = int(line[0]) 
        y = int(line[1]) 
        time = int(line[2])
        objectType = int(line[3]) 
        hitsound = int(line[4])  

        hitobject = None

        # Circle
        if 1 & int(objectType): 
            hitobject = Circle(x, y, time, objectType, hitsound)
            if len(line) > 5:
                hitobject.hitsample = line[5]

        # Slider      
        if 2 & int(objectType):
            hitobject = Slider(x, y, time, objectType, hitsound)
            
            curveSplit = line[5].split("|")
            
            hitobject.curveType = curveSplit[0]
            for i in range(1, len(curveSplit)):
                vectorSplit = curveSplit[i].split(":")
                hitobject.curvePoints.append(Point(int(vectorSplit[0]), int(vectorSplit[1])))
                        
            hitobject.slides = int(line[6])
            hitobject.length = float(line[7])

            if len(line) > 8:
                hitobject.edgeSounds = line[8]
                hitobject.edgeSets = line[9]
                hitobject.hitsample = line[10]


            uninheritedPoint = getUninheritedPoint(self.timingPoints, hitobject.time)
            inheritedPoint = getInheritedPoint(self.timingPoints, uninheritedPoint, hitobject.time)
            if inheritedPoint == None:
                hitobject.calcDuration(self.difficulty["SliderMultiplier"], uninheritedPoint.beatLength, 1)
            else:
                hitobject.calcDuration(self.difficulty["SliderMultiplier"], uninheritedPoint.beatLength, fileToSvm(inheritedPoint.beatLength))
                                
        if 8 & int(objectType): # Spinner          
            hitobject = Spinner(x, y, time, objectType, hitsound)
            hitobject.endtime = int(line[5])
            if len(line) > 6:
                hitobject.hitsample = line[6]

        
        self.hitobjects.append(hitobject)


    def replaceHitObject(self, hitobject):
        
        for i in range(0, len(self.hitobjects)):
            if self.hitobjects[i].time == hitobject.time:
                self.hitobjects[i] = hitobject
                return True
            
        return False
            
    def addTimingPoint(self, timingPoint):

        insert_index = 0

        for i in range(0, len(self.timingPoints)):
            if self.timingPoints[i].time == timingPoint.time and self.timingPoints[i].type == timingPoint.type:
                self.timingPoints[i] = timingPoint
                return
            
            elif self.timingPoints[i].time > timingPoint.time:
                self.timingPoints.insert(i, timingPoint)
                return

            insert_index = i

        self.timingPoints.insert(insert_index, timingPoint)
        
        
    # Writing to file and naming it properly
    def writeFile(self):
            
        fileLine = self.osuFileVersion + "\n\n"
        
        # Insert [General] section
        fileLine += "[General]\n"
        for k, v in self.general.items():
            fileLine += k + ":" + str(v) + "\n"
        fileLine += "\n"

        # Insert [Editor] section
        fileLine += "[Editor]\n"
        for k, v in self.editor.items():
            if k == "Bookmarks":
                fileLine += k + ":" + ",".join(v) + "\n"
            else:
                fileLine += k + ":" + str(v) + "\n"
        fileLine += "\n"

        # Insert [Metadata] section
        fileLine += "[Metadata]\n"
        for k, v in self.metadata.items():
            if k == "Tags":
                fileLine += k + ":" + " ".join(v) + "\n"
            else:
                fileLine += k + ":" + str(v) + "\n"
        fileLine += "\n"

        # Insert [Difficulty] section
        fileLine += "[Difficulty]\n"
        for k, v in self.difficulty.items():
            fileLine += k + ":" + str(v) + "\n"
        fileLine += "\n"

        # Insert [Events] section
        fileLine += "[Events]\n"
        for i in self.events:
            fileLine += i + "\n"
        fileLine += "\n"


        # Insert [TimingPoints] section
        fileLine += "[TimingPoints]\n"
        for i in self.timingPoints:
            fileLine += str(i.time) + ","
            if i.type == 1:
                fileLine += str(i.beatLength)
            elif i.type == 0:
                fileLine += str(i.beatLength)

            fileLine += "," + str(i.meter) + "," + str(i.sampleSet) + "," + str(i.sampleIndex) + "," + str(i.volume) + "," + str(i.type) + "," + str(i.effect) + "\n"
        fileLine += "\n"

        # Insert [Colours] section
        if self.colours:
            fileLine += "[Colours]\n"
            for k, v in self.colours.items():
                fileLine += k + ":" + v + "\n"
            fileLine += "\n"

        # Insert [HitObjects] section
        fileLine += "[HitObjects]\n"
        for i in self.hitobjects:
            fileLine += str(i.x) + "," + str(i.y) + "," + str(i.time) + "," + str(i.type) + "," + str(i.hitsound)
            
            # Circle
            if i.type & 1:
                if i.hitsample != None:
                    fileLine += "," + str(i.hitsample)

            # Slider
            if i.type & 2:
                fileLine += "," + str(i.curveType)
                for j in i.curvePoints:
                    fileLine += "|" + str(int(j.x)) + ":" + str(int(j.y))
                fileLine += "," + str(i.slides) + "," + str(i.length)

                if(i.hitsample != None):
                    fileLine += "," + str(i.edgeSounds) + "," + str(i.edgeSets) + "," + str(i.hitsample)

            # Spinner
            if i.type & 8:
                fileLine += "," + str(i.endtime)
                if(i.hitsample != None):
                    fileLine += "," + str(i.hitsample)

            fileLine += "\n"

        fileLine += "\n"

        self.filename = self.filename.replace("<", "")
        self.filename = self.filename.replace(">", "")
        self.filename = self.filename.replace("?", "")
        with open(self.path + self.filename, "w+", encoding="utf-8") as fileOut:
            fileOut.write(fileLine)

