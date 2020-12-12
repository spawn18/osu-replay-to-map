import math
import copy
from utils import Point, fileToSvm

class TimingPoint:
    def __init__(self, time, beatLength, meter, sampleSet, sampleIndex, volume, uninherited, effects):
        self.time = time
        self.meter = meter
        self.sampleSet = sampleSet
        self.sampleIndex = sampleIndex
        self.volume = volume
        self.uninhetied = uninheried
        self.effects = effects
        
class HitObject:
    Circle = 1
    Slider = 2
    Spinner = 8

    def __init__(self, x, y, time, type_, hitSound):
        self.x = x
        self.y = y
        self.time = time
        self.type = type_
        self.hitSound = hitSound

    def flip():
        self.y = screen_height - self.y

        
class Spinner(HitObject):
    def __init__(self, x, y, time, type_, hitSound):
        super().__init__(x, y, time, type_, hitSound)
        self.endTime = endTime
        self.hitSample = hitSample
        
class Circle(HitObject):
    def __init__(self, x, y, time, type_, hitSound):
        super().__init__(x, y, time, type_, hitSound)
        self.hitsample = None
        
class Slider(HitObject):
    def __init__(self, x, y, time, type_, hitSound, curveType):
        super().__init__(x, y, time, type_, hitSound)
        self.curveType = curveType
        self.curvePoints = list()
        self.slides = None
        self.length = None
        self.edgeSounds = None
        self.edgeSets = None
        self.hitsample = None
            
    #def calcDuration(self, beatmapSV, uninheritedPoint, inheritedPoint):
        #self.duration = (self.length / (beatmapSV * inheritedPoint.beatLength * 100)) * self.slides * uninheritedPoint.beatLength

    def flip():
        super().flip()
        for i in self.curvePoints:
            i.y = screen_height - i.y
                                                                                                                                                    
        
